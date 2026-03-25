import MySQLdb
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    """Database connection and operations"""
    
    def __init__(self, host, user, password, db):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
    
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

    def update_user(self, user_id, name, email, password=None, bio=None):
        """Update user profile details"""
        conn = self.get_connection()
        if not conn:
            return False

        cursor = conn.cursor()
        try:
            if password and bio is not None:
                hashed_password = generate_password_hash(password)
                cursor.execute(
                    "UPDATE users SET name=%s, email=%s, password=%s, bio=%s WHERE id=%s",
                    (name, email, hashed_password, bio, user_id)
                )
            elif password:
                hashed_password = generate_password_hash(password)
                cursor.execute(
                    "UPDATE users SET name=%s, email=%s, password=%s WHERE id=%s",
                    (name, email, hashed_password, user_id)
                )
            elif bio is not None:
                cursor.execute(
                    "UPDATE users SET name=%s, email=%s, bio=%s WHERE id=%s",
                    (name, email, bio, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET name=%s, email=%s WHERE id=%s",
                    (name, email, user_id)
                )

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
            cursor.execute("SELECT id, name, email, password, plan, bio, theme FROM users WHERE email = %s", (email,))
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
            cursor.execute("SELECT id, name, email, plan, bio FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            return result
        finally:
            cursor.close()
            conn.close()
    
    def verify_password(self, stored_hash, password):
        """Verify password hash"""
        return check_password_hash(stored_hash, password)
    
    # File operations
    def upload_file(self, user_id, filename):
        """Record uploaded file"""
        conn = self.get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO uploaded_files (user_id, filename, upload_date) VALUES (%s, %s, NOW())",
                (user_id, filename)
            )
            conn.commit()
            return cursor.lastrowid
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
            cursor.execute("SELECT id, user_id, filename FROM uploaded_files WHERE id = %s", (file_id,))
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

