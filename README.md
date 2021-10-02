# Heroku Line Einstein Vision

環境変数
- EINSTEIN_VISION_ACCOUNT_ID
- EINSTEIN_VISION_URL
- EINSTEIN_VISION_MODEL_ID
- EINSTEIN_VISION_PRIVATE_KEY // 開発環境ではファイルに設置する
- LINE_ACCESS_TOKEN
- LINE_ACCESS_SECRET

アプリケーション環境変数
- DATABASE_URL
- DISABLE_COLLECTSTATIC=1
- SECRET_KEY={ランダム文字列}


EINSTEIN_VISIONのセットアップ内容

データセットをアップロードする

`python manage.py datasets_upload --path ファイルパス --name 任意名`

正しく登録されたか確認

`python manage.py datasets_confirm 1234567(datasets_id)`

モデルを作成
`python manage.py train_create 1234567(datasets_id)`

モデルが作成されたか確認
`python manage.py train_confirm H55EZDPXXMSPR7KXRHKMQMOCPQ(model_id)`

完了後、ModelIDをEINSTEIN_VISION_MODEL_IDにセットする
