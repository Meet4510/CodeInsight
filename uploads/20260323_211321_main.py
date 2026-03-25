import sys
from PySide6.QtWidgets import QApplication

from src.f1_data import (
    get_race_telemetry,
    enable_cache,
    get_circuit_rotation,
    load_session,
    get_quali_telemetry,
    list_rounds,
    list_sprints
)

from src.arcade_replay import run_arcade_replay
from src.interfaces.qualifying import run_qualifying_replay
from src.cli.race_selection import cli_load
from src.gui.race_selection import RaceSelectionWindow


# --------------------------------------------------
# Core replay logic
# --------------------------------------------------

def main(
    year=None,
    round_number=None,
    playback_speed=1,
    session_type='R',
    visible_hud=True,
    ready_file=None
):
    # Enable cache FIRST
    enable_cache()

    print(f"Loading F1 {year} Round {round_number} Session '{session_type}'")

    session = load_session(year, round_number, session_type)

    print(
        f"Loaded session: "
        f"{session.event['EventName']} - "
        f"{session.event['RoundNumber']} - "
        f"{session_type}"
    )

    # --------------------------------------------------
    # QUALIFYING / SPRINT QUALIFYING
    # --------------------------------------------------

    if session_type in ('Q', 'SQ'):

        qualifying_session_data = get_quali_telemetry(
            session,
            session_type=session_type
        )

        title = (
            f"{session.event['EventName']} - "
            f"{'Sprint Qualifying' if session_type == 'SQ' else 'Qualifying Results'}"
        )

        run_qualifying_replay(
            session=session,
            data=qualifying_session_data,
            title=title,
            ready_file=ready_file
        )

        return

    # --------------------------------------------------
    # RACE / SPRINT
    # --------------------------------------------------

    race_telemetry = get_race_telemetry(session, session_type=session_type)

    # Attempt to load qualifying lap for track layout (DRS zones)
    example_lap = None

    try:
        print("Attempting to load qualifying session for track layout...")
        quali_session = load_session(year, round_number, 'Q')

        if quali_session is not None and len(quali_session.laps) > 0:
            fastest_quali = quali_session.laps.pick_fastest()

            if fastest_quali is not None:
                quali_telemetry = fastest_quali.get_telemetry()

                if 'DRS' in quali_telemetry.columns:
                    example_lap = quali_telemetry
                    print(
                        f"Using qualifying lap from driver "
                        f"{fastest_quali['Driver']} for DRS zones"
                    )

    except Exception as e:
        print(f"Could not load qualifying session: {e}")

    # Fallback: fastest race lap
    if example_lap is None:
        fastest_lap = session.laps.pick_fastest()

        if fastest_lap is None:
            print("Error: No valid laps found in session")
            return

        example_lap = fastest_lap.get_telemetry()
        print("Using fastest race lap (speed-based DRS fallback)")

    drivers = session.drivers
    circuit_rotation = get_circuit_rotation(session)

    run_arcade_replay(
        frames=race_telemetry['frames'],
        track_statuses=race_telemetry['track_statuses'],
        example_lap=example_lap,
        drivers=drivers,
        playback_speed=playback_speed,
        driver_colors=race_telemetry['driver_colors'],
        title=f"{session.event['EventName']} - {'Sprint' if session_type == 'S' else 'Race'}",
        total_laps=race_telemetry['total_laps'],
        circuit_rotation=circuit_rotation,
        visible_hud=visible_hud,
        ready_file=ready_file
    )


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":

    # ---------------- GUI ----------------
    if "--gui" in sys.argv:
        app = QApplication(sys.argv)
        win = RaceSelectionWindow()
        win.show()
        sys.exit(app.exec())

    # ---------------- CLI ----------------
    if "--cli" in sys.argv:
        cli_load()
        sys.exit(0)

    # ---------------- Argument parsing ----------------

    year = 2025
    round_number = 12
    playback_speed = 1
    visible_hud = "--no-hud" not in sys.argv

    if "--year" in sys.argv:
        year = int(sys.argv[sys.argv.index("--year") + 1])

    if "--round" in sys.argv:
        round_number = int(sys.argv[sys.argv.index("--round") + 1])

    if "--list-rounds" in sys.argv:
        list_rounds(year)
        sys.exit(0)

    if "--list-sprints" in sys.argv:
        list_sprints(year)
        sys.exit(0)

    # Session type resolution
    if "--sprint-qualifying" in sys.argv:
        session_type = 'SQ'
    elif "--sprint" in sys.argv:
        session_type = 'S'
    elif "--qualifying" in sys.argv:
        session_type = 'Q'
    else:
        session_type = 'R'

    # Optional ready-file (used by GUI)
    ready_file = None
    if "--ready-file" in sys.argv:
        idx = sys.argv.index("--ready-file") + 1
        if idx < len(sys.argv):
            ready_file = sys.argv[idx]

    # ---------------- Run ----------------
    main(
        year=year,
        round_number=round_number,
        playback_speed=playback_speed,
        session_type=session_type,
        visible_hud=visible_hud,
        ready_file=ready_file
    )
