# MAKEFILE
MODULE_NAME:=omi_async_http_client
TEST_CASE_DIR:=`pwd`/test


run:
	python mock_fastapi.py

install:
	python setup.py install

coverage:
	cd ${TEST_CASE_DIR} && \
    pytest ./test* --cov=${MODULE_NAME} --cov-report=html
    
unittest:
	cd ${TEST_CASE_DIR} && \
    pytest ./test_unit*

integration_test:
	cd ${TEST_CASE_DIR} && \
    pytest ./test_integration*

echo:
	echo ${MODULE_NAME}