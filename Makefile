.PHONY: server
.PHONY: pep8
.PHONY: freeze

server:
	python manage.py runserver 8000

freeze:
	pip freeze > requirements.txt

pep8: ## pep8フォーマットに変換
	@pep8 . | cut -d: -f 1 | sort | uniq | xargs autopep8 -i

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
