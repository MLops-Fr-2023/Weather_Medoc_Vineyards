name: Pytest

on:
  push:
    branches:
      - main
      - develop
      - develop_gh_actions
  pull_request: {}  # Trigger the workflow for all pull requests

jobs:
  test:
    name: Run Pytest
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: [3.7, 3.8, 3.9, 3.10, 3.11]

    steps:
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}

    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Docker
      uses: docker/setup-buildx-action@v2

    - name: Test Backend
      run: |
        docker-compose -f Backend/docker-compose.test.yml build  # Build the pytest service defined in docker-compose.test.yml
        docker-compose -f Backend/docker-compose.test.yml up -d  # Start the pytest service in detached mode
        docker-compose -f Backend/docker-compose.test.yml run \
        -e SECRET_KEY=${{ secrets.SECRET_KEY }} \
        -e ALGORITHM=${{ secrets.ALGORITHM }} \
        -e WEATHER_API_KEY=${{ secrets.WEATHER_API_KEY }} \
        -e FILE_ID=${{ secrets.FILE_ID }} \
        -e WAREHOUSE_SNOWFLAKE=${{ secrets.WAREHOUSE_SNOWFLAKE }} \
        -e DB_SNOWFLAKE=${{ secrets.DB_SNOWFLAKE }} \
        -e SCHEMA_SNOWFLAKE=${{ secrets.SCHEMA_SNOWFLAKE }} \
        -e AWS_ACCESS_KEY_ID=${{ secrets.ACCESS_KEY_ID }} \
        -e AWS_SECRET_ACCESS_KEY=${{ secrets.AWS_SECRET_ACCESS_KEY }} \
        -e AWS_DEFAULT_REGION=${{ secrets.AWS_DEFAULT_REGION }} \
        -e BUCKET_NAME=${{ secrets.BUCKET_NAME }} \
        pytest  # Run the pytest command inside the pytest service

    - name: Clean up Docker
      if: always()
      run: docker-compose -f Backend/docker-compose.test.yml down  # Stop and remove the containers and network
