import MySQLdb
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    """Database connection and operations"""
    
    def __init__(self, host, user, password, db):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.ensure_account_status_column()
        self.ensure_uploaded_files_stored_filename_column()

    def ensure_account_status_column(self):
        """Ensure users.account_status exists for block/unblock controls."""
        conn = self.get_connection()
        if not conn:
            return

        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s
                  AND TABLE_NAME = 'users'
                  AND COLUMN_NAME = 'account_status'
                """,
                (self.db,)
            )
            exists = cursor.fetchone()
            if exists and exists[0] == 0:
                cursor.execute(
                    "ALTER TABLE users ADD COLUMN account_status VARCHAR(20) NOT NULL DEFAULT 'active'"
                )
                conn.commit()
        finally:
            cursor.close()
            conn.close()

    def ensure_uploaded_files_stored_filename_column(self):
        """Ensure uploaded_files.stored_filename exists for safe unique storage."""
        conn = self.get_connection()
        if not conn:
            return

        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s
                  AND TABLE_NAME = 'uploaded_files'
                  AND COLUMN_NAME = 'stored_filename'
                """,
                (self.db,)
            )
            exists = cursor.fetchone()
            if exists and exists[0] == 0:
                cursor.execute(
                    "ALTER TABLE uploaded_files ADD COLUMN stored_filename VARCHAR(255) DEFAULT NULL AFTER filename"
                )
                conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def get_connection(self):
        """Create and return database connection"""
        try:
            conn = MySQLdb.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.db
            )
            return conn
        except MySQLdb.Error as e:
            print(f"Database connection error: {e}")
            return None
    
    # User operations
    def register_user(self, name, email, password):
        """Register a new user"""
        conn = self.get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        try:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, hashed_password)
            )
            conn.commit()
            result = cursor.lastrowid
            return result
        except MySQLdb.IntegrityError:
            return None
        finally:
            cursor.close()
            conn.close()

    def update_user(self, user_id, name, email, password=None, bio=None, avatar=None):
        """Update user profile details"""
        conn = self.get_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        try:
            # Build SET clause dynamically
            fields = ["name=%s", "email=%s"]
            values = [name, email]

            if password:
                fields.append("password=%s")
                values.append(generate_password_hash(password))
            if bio is not None:
                fields.append("bio=%s")
                values.append(bio)
            if avatar is not None:
                fields.append("avatar=%s")
                values.append(avatar if avatar != '' else None)

            values.append(user_id)
            sql = "UPDATE users SET " + ", ".join(fields) + " WHERE id=%s"
            cursor.execute(sql, tuple(values))
            conn.commit()
            return cursor.rowcount > 0
        except MySQLdb.IntegrityError:
            return False
        finally:
            cursor.close()
            conn.close()

    def get_user_by_email(self, email):
        """Get user by email"""
        conn = self.get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, name, email, password, plan, role, bio, avatar, account_status FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()
            return result
        finally:
            cursor.close()
            conn.close()
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, name, email, plan, role, bio, avatar, account_status FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            return result
        finally:
            cursor.close()
            conn.close()
    
    def get_total_users(self):
        """Return total user count"""
        conn = self.get_connection()
        if not conn:
            return 0
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM users")
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            cursor.close()
            conn.close()
    
    def get_active_subscriptions(self):
        """Return count of non-free plans"""
        conn = self.get_connection()
        if not conn:
            return 0
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM users WHERE plan IS NOT NULL AND LOWER(plan) != 'free'")
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            cursor.close()
            conn.close()
    
    def get_analyses_today(self):
        """Return number of analyses created today"""
        conn = self.get_connection()
        if not conn:
            return 0
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM analysis_results WHERE DATE(created_at) = CURDATE()"
            )
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            cursor.close()
            conn.close()
    
    def get_weekly_signups(self):
        """Return signup counts for Monday through Sunday in the current week"""
        conn = self.get_connection()
        if not conn:
            return []
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT CURDATE() - INTERVAL WEEKDAY(CURDATE()) DAY")
            week_start_row = cursor.fetchone()
            week_start = week_start_row[0] if week_start_row else None

            if not week_start:
                return []

            labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            results = []
            for offset, label in enumerate(labels):
                day_start = week_start + timedelta(days=offset)
                day_end = day_start + timedelta(days=1)
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE created_at >= %s AND created_at < %s",
                    (day_start, day_end)
                )
                count_row = cursor.fetchone()
                count = count_row[0] if count_row else 0
                results.append({'label': label, 'count': count})
            return results
        finally:
            cursor.close()
            conn.close()
    
    def get_recent_audits(self, limit=5):
        """Return recent analysis results joined with file data"""
        conn = self.get_connection()
        if not conn:
            return []
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT uf.filename, ar.score, ar.complexity, ar.maintainability, ar.issues, ar.created_at "
                "FROM analysis_results ar "
                "JOIN uploaded_files uf ON ar.file_id = uf.id "
                "ORDER BY ar.created_at DESC "
                "LIMIT %s",
                (limit,)
            )
            results = cursor.fetchall()
            return results
        finally:
            cursor.close()
            conn.close()

    def get_users_for_admin(self, include_admins=True):
        """Return user records for admin management views."""
        conn = self.get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        try:
            if include_admins:
                cursor.execute(
                    "SELECT id, name, email, plan, role, account_status, created_at FROM users ORDER BY id DESC"
                )
            else:
                cursor.execute(
                    "SELECT id, name, email, plan, role, account_status, created_at FROM users WHERE role != 'admin' ORDER BY id DESC"
                )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def set_user_block_status(self, user_id, blocked=True):
        """Set user account status to blocked/active."""
        conn = self.get_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        try:
            new_status = 'blocked' if blocked else 'active'
            cursor.execute(
                "UPDATE users SET account_status = %s WHERE id = %s",
                (new_status, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    
    def verify_password(self, stored_hash, password):
        """Verify password hash"""
        return check_password_hash(stored_hash, password)
    
    # File operations
    def upload_file(self, user_id, filename, stored_filename=None):
        """Record uploaded file"""
        conn = self.get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO uploaded_files (user_id, filename, stored_filename, upload_date) VALUES (%s, %s, %s, NOW())",
                (user_id, filename, stored_filename)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()
    
    def delete_file(self, file_id, user_id):
        """Delete a file record (and cascades to analysis_results via FK)"""
        conn = self.get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        try:
            # Ensure the file belongs to the user before deleting
            cursor.execute(
                "DELETE FROM uploaded_files WHERE id = %s AND user_id = %s",
                (file_id, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def get_user_files(self, user_id):
        """Get all files for a user"""
        conn = self.get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, filename, upload_date FROM uploaded_files WHERE user_id = %s ORDER BY upload_date DESC",
                (user_id,)
            )
            results = cursor.fetchall()
            return results
        finally:
            cursor.close()
            conn.close()
    
    def get_file_by_id(self, file_id):
        """Get file details by ID"""
        conn = self.get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, user_id, filename, stored_filename FROM uploaded_files WHERE id = %s", (file_id,))
            result = cursor.fetchone()
            return result
        finally:
            cursor.close()
            conn.close()
    
    # Analysis results operations
    def save_analysis_result(self, file_id, score, complexity, maintainability, issues, suggestions):
        """Save or update analysis result"""
        conn = self.get_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO analysis_results 
                    (file_id, score, complexity, maintainability, issues, suggestions)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    score=VALUES(score),
                    complexity=VALUES(complexity),
                    maintainability=VALUES(maintainability),
                    issues=VALUES(issues),
                    suggestions=VALUES(suggestions),
                    updated_at=NOW()
                """,
                (file_id, score, complexity, maintainability, issues, suggestions)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()
    
    def get_analysis_result(self, file_id):
        """Get analysis result for a file"""
        conn = self.get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM analysis_results WHERE file_id = %s", (file_id,))
            result = cursor.fetchone()
            return result
        finally:
            cursor.close()
            conn.close()
    
    def get_user_analysis_history(self, user_id):
        """Get user's analysis history"""
        conn = self.get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        try:
            cursor.execute(
                """SELECT ar.id, uf.filename, ar.score, ar.upload_date 
                   FROM analysis_results ar
                   JOIN uploaded_files uf ON ar.file_id = uf.id
                   WHERE uf.user_id = %s
                   ORDER BY uf.upload_date DESC""",
                (user_id,)
            )
            results = cursor.fetchall()
            return results
        finally:
            cursor.close()
            conn.close()

    def generate_reset_token(self, email, token):
        """Generate and store password reset token"""
        conn = self.get_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        try:
            # Token expires in 1 hour
            cursor.execute(
                "UPDATE users SET reset_token=%s, reset_token_expires=DATE_ADD(NOW(), INTERVAL 1 HOUR) WHERE email=%s",
                (token, email)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def verify_reset_token(self, token):
        """Verify reset token and return user if valid"""
        conn = self.get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, name, email FROM users WHERE reset_token=%s AND reset_token_expires > NOW()",
                (token,)
            )
            result = cursor.fetchone()
            return result
        finally:
            cursor.close()
            conn.close()

    def reset_password(self, email, new_password):
        """Reset user password and clear token"""
        conn = self.get_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        try:
            hashed_password = generate_password_hash(new_password)
            cursor.execute(
                "UPDATE users SET password=%s, reset_token=NULL, reset_token_expires=NULL WHERE email=%s",
                (hashed_password, email)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()