run-test:
    PYTHONPATH=src pytest -svv 
run-test-coverage:
    PYTHONPATH=src pytest -svv --cov=src --cov-report=term-missing --cov-report=html
run-test-filter TEST:
    PYTHONPATH=src pytest -svv -k "{{TEST}}"
lint:
    ruff format src tests
    ruff check src tests --fix --exit-zero --line-length 100 --target-version py38
    
install-requirement:
    pip install -r requirements.txt
list:
    mpremote ls
upload:
    mpremote mkdir :lib || echo "Directory already exists."
    mpremote cp src/async_fsm/*.py :lib/async_fsm/
    # just to check if the files are uploaded
    mpremote ls :lib/async_fsm/