# まるたいスタンプラリー - かんたん版

この版は **Supabase・SQL・Secrets・Database Passwordの設定が不要** です。
GitHubへアップロードして、Streamlit Community Cloudで `app.py` をDeployすれば起動します。

## 使うもの

- Streamlit
- CSV: 施設データ
- SQLite: 訪問履歴
- アプリ内フォルダ: 元写真 / スタンプ入り写真
- OpenStreetMap + Folium: 地図
- Pillow: 「たい」スタンプ合成

## Deploy手順

1. このフォルダの中身をGitHubリポジトリ `marutai-stamp-rally` に上書きアップロードします。
2. Streamlit Community Cloudで以下を指定します。
   - Repository: `chamaboo2/marutai-stamp-rally`
   - Branch: `main`
   - Main file path: `app.py`
3. `Deploy` を押します。

**Secretsの入力は不要です。Supabaseの設定も不要です。**

## 施設データ

`data/facilities.csv` で管理します。最初は画面確認用の「施設データ例」が3件入っています。
実在施設データを入れるときは、このCSVを置き換えてください。

必要列:

`id,name,category,ward,address,latitude,longitude,has_open_air_bath,has_natural_hot_spring,website_url,active`

category:
- `sento`
- `super_sento`
- `spa`
- `other`

## 写真と訪問履歴

- 訪問履歴: `data/marutai.db`
- 元写真: `storage/original/`
- スタンプ写真: `storage/stamped/`

## 重要な制約

Streamlit Community Cloudのローカル保存領域は永続保存を保証しません。アプリ再起動・再デプロイ等で訪問記録や写真が消える可能性があります。

そのため、この「かんたん版」はまずアプリを完成・確認するためのMVPです。継続利用する段階になったら、データ保存だけSupabase等へ移行します。UIや画面構成はそのまま利用できます。

## 正式ロゴ

正式ロゴを `assets/logo.png` に置けば自動表示します。未配置時は代替ロゴを表示します。
`assets/tai_stamp.png` は訪問写真へ押す「たい」スタンプです。
