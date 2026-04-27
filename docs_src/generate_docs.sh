#!/bin/bash

# プロジェクトルートディレクトリへのパスを取得
PROJECT_ROOT=$(dirname $(dirname $(realpath $0)))

# srcディレクトリのPythonモジュールに対してドキュメントを生成
sphinx-apidoc -o $PROJECT_ROOT/docs_src/source $PROJECT_ROOT/src/asymmvelo

# SphinxでHTMLドキュメントをビルド
make html


