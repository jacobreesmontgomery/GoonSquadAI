# GoonSquadAI
This BFF-architected, AI-powered application takes advantage of the Strava API to acquire running data on authenticated athletes and present it in valuable ways to the users.

## Pages

### Main Page

This page will be comprised of...

1. A card component for each athlete that can be clicked on to go to specific stats and data visualizations for the given athlete.
2. A menu linking the following...
   1. A 'Basic Stats' page.
   2. A 'Database' page.
   3. A 'Chat' page.

### Athlete Data

This page will hold specific data to the athlete selected on the main page. A user will only be directed to this page if they click on a card component from the main page.

### Basic Stats

This page will hold basic week recap stats, pulled from the `strava_api.activities` DB table.

### Database

This page will have a filterable table to hold all runs stored in the `strava_api.activities` DB table. The user will be able to filter by all columns.

### Chat

In a traditional chatbot interface, the user will be able to ask questions about their training and receive intelligent, GenAI-driven answers. This feature will largely by driven by a TAG, or Table Augmented Generation, mechanism.

## App startups

Follow these steps to get everything up and running:

1. Ensure you're using the virtual environment: `.venv\Scripts\Activate.ps1`.
2. In one terminal, navigate to the [react](.) directory and run `npm start`.
3. In another terminal, navigate to the Node server, [backend.js](./backend.js), and run `npm start`.
4. In a third terminal, navigate to the FastAPI backend server, [app.py](./python/app.py), and run one of two commands:
   - Reload on code changes: `uvicorn app:app --reload`
   - No reload: `TBD`

## GENERAL APP FLOW

### AUTHENTICATION FLOW
1. A user authenticates with the app by clicking the 'Authenticate' button on the FE.
2. The request is routed from the FE to the BE NodeJS server, `server.js`.
3. The NodeJS server receives the request and routes it to the BE FastAPI server.
4. The BE FastAPI endpoint receives the request and adds the newly authenticated user to the `strava_api.athletes` DB table.
5. Going forward, the new user's activities will be acquired on a scheduled frequency, going into the `strava_api.activities` DB table.

## Data Acquisition

Data has been acquired from 1/1/23 onward. Currently, the following data is captured for each activity:

| Field | Description |
| ----- | ----------- |
| activity_id | Unique identifier for the activity |
| athlete_id | Athlete associated with the activity |
| name | Name of the activity |
| moving_time | Time spent moving (HH:MM:SS) |
| moving_time_s | Moving time in seconds |
| distance_mi | Distance covered in miles |
| pace_min_mi | Average pace in minutes per mile |
| avg_speed_ft_s | Average speed in feet per second |
| full_datetime | Full timestamp of the activity |
| time | Time of day when the activity took place |
| week_day | Day of the week (MON-SUN) |
| month | Month of the year (1-12) |
| day | Day of the month (1-31) |
| year | Year of the activity |
| spm_avg | Average steps per minute |
| hr_avg | Average heart rate during the activity |
| wkt_type | Run type classification (0=default, 1=race, 2=long run, 3=workout) |
| description | Additional notes or description of the activity |
| total_elev_gain_ft | Total elevation gain in feet |
| manual | Whether the activity was manually logged |
| max_speed_ft_s | Maximum speed in feet per second |
| calories | Calories burned during the activity |
| achievement_count | Number of achievements earned |
| kudos_count | Number of kudos received |
| comment_count | Number of comments received |
| athlete_count | Number of athletes involved in the activity |
| rpe | Rate of perceived exertion (1-10) |
| rating | User rating of the activity (1-10) |
| avg_power | Average power output in watts |
| sleep_rating | Sleep rating on the day of activity (1-10) |

## DB Migrations

Follow these steps to run a migration via Alembic:
1. Make the desired DB changes within the [./python/dao](./python/dao/) folder.
2. Run `alembic revision --autogenerate -m "Revision message"`.
3. Validate the generated migration file(s) within the [versions](./migrations/versions/) directory.
4. Run `alembic upgrade head` to execute the DB changes via the [configured](./migrations/env.py) DB engine.
5. Validate the changes in the target DB.

**NOTE**: If necessary, you can downgrade the most recent upgrade by running `alembic downgrade -1`.