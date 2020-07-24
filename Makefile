# MAKEFILE
MODULE_NAME:=omi_async_http_client
TEST_CASE_DIR:=`pwd`/test

install:
	python setup.py install

coverage:
	cd ${TEST_CASE_DIR} && \
    pytest --cov=${MODULE_NAME} --cov-report=html ./test*
    
unittest:
	cd ${TEST_CASE_DIR} && \
    pytest ./test*

echo:
	echo ${MODULE_NAME}