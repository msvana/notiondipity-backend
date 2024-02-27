#!/usr/bin/env bash

TEST=$1

if [ "$TEST" == "test" ]; then
	PORT=10001
	APP=notiondipity-postgres-test
else
	PORT=10000
	APP=notiondipity-postgres
fi

fly proxy $PORT:5432 -a $APP

