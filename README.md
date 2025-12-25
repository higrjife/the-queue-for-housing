# The Queue for Housing (Очередь на жилье)


## Description
A housing waiting list system with automatic priority calculation. Automates the process of distributing state or municipal apartments.

## Key functions: 
-  ✅ Registration of housing applications with indication of living conditions
-  ✅ Automatic calculation of queue priority based on criteria (income, number of children, disability, etc.)
-  ✅ Checking availability of available housing
-  ✅ History of changes in application statuses
-  ✅ Automatic notifications about progress in the queue (optional)
-  ✅ The admin panel for data management,Issuing notifications about the need to update documents

# Python for Data Analysis

This small Django app collects and exposes simple statistics about the housing queue project. It is intended to provide quick, high-level numbers and basic charts (e.g., total applications, open housing units, recent queue activity) so instructors and reviewers can understand system behavior without digging into raw data.

Why it exists
------------

- Give a concise snapshot of the system's state for demonstrations and grading.
- Provide a few lightweight endpoints/views that the frontend or tests can query for aggregated values.

Where to look (quick)
---------------------

- Views: `app_statistics/views.py` — endpoints that return numbers or simple JSON for charts. This is the main file which uses pandas, matplotlib, numpy to compute statistics.
- URLs: `app_statistics/urls.py` — the routes you can visit during demos or tests.
- Data: `house_data.csv` — sample dataset used for testing and demos.

How a teacher should use it
--------------------------

- Open the statistics page in the running site to see the dashboard summary.
- Read the `app_statistics/views.py` file to understand what data is being aggregated.

Notes
-----

- This app is intentionally small and read-only: heavy aggregation should be done offline or in management commands.
- For details about specific endpoints, inspect `views.py` and `urls.py`.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/higrjife/the-queue-for-housing.git
    ```
2. Navigate to the project directory:
    ```bash
    cd the-queue-for-housing
    ```
3. Create a virtual environment:
    ```bash
    python -m venv venv
    ```
4. Install the dependencies:
    ```bash
    python -m pip install -r requirements.txt
    ```

## Usage

1. Start the development server:
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```
2. Open your browser and navigate to `http://localhost:8000`.

## Telegram bot

1. Create a bot using the BotFather on Telegram and get the token.
2. Add the token to your environment variables or directly in the code.
3. Create .env file in the telegram_bot directory and add the following variables:
    ```env
    TELEGRAM_BOT_TOKEN=your_token_here
    ```
4. Telegram Bot is located in telegram_bot directory.
    ```bash
    cd telegram_bot
    ```
5. Install the required libraries:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```
6. Run the bot script:
    ```bash

    python bot.py
    ```