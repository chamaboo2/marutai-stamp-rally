# GitHub Actions で Supabase を初期化する手順

1. GitHub リポジトリにこのプロジェクト一式をアップロードします。
2. GitHub の Settings > Secrets and variables > Actions を開きます。
3. New repository secret を押します。
4. Name に `SUPABASE_DB_URL`、Secret に Supabase の PostgreSQL connection string を登録します。
5. GitHub の Actions タブを開きます。
6. 左側の `Setup Supabase` を選びます。
7. `Run workflow` > `Run workflow` を押します。
8. 緑のチェックが付けば初期化完了です。

この処理で `facilities`、`visits`、`visit-photos` を作成し、`data/facilities.csv` を取り込みます。
