# まるたいスタンプラリー MVP

東京23区の銭湯・スーパー銭湯・日帰り温浴施設を親子で巡り、写真と「たい」スタンプで記録する Streamlit MVP です。

## 実装済み

- トップ画面：地図、露天風呂検索、スタンプ帳、行ってきた！
- OpenStreetMap + Folium の施設地図
- 区、露天風呂、天然温泉、施設種類、訪問状態フィルター
- 施設一覧・施設詳細
- カメラ撮影 / 写真アップロード
- Pillow による「○たい」+ 訪問日の写真合成
- 元写真 / スタンプ写真を別保存
- Supabase PostgreSQL の facilities / visits
- Supabase Storage の original/ / stamped/ 分離
- スタンプ帳：新しい順、古い順、区ごと、施設名順
- 同一施設への複数訪問
- 訪問済み施設を地図上で赤い「たい」マーカー表示
- 訪問数を「○湯」で表示
- Supabase 未設定時はセッション内デモモードで起動

## 重要：正式ロゴ

正式ロゴ画像そのものは今回の添付に独立ファイルとして含まれていません。画面モックから切り出した画像を正式ロゴとして再利用・再生成することはしていません。

`assets/logo.png` に正式ロゴをそのまま配置してください。存在する場合は自動で表示されます。未配置時のみ文字ベースの代替表示になります。

`assets/tai_stamp.png` は写真へ押す訪問スタンプ用で、正式ロゴとは別データです。

## 1. Supabase を作る

Supabase の SQL Editor で `sql/001_schema.sql` を実行します。

作成されるもの：

- `public.facilities`
- `public.visits`
- private Storage bucket `visit-photos`

MVP は Streamlit サーバーから Service Role Key を利用する前提です。Service Role Key はブラウザへ渡さず、GitHub へコミットしないでください。

## 2. Secrets を設定する

Streamlit Community Cloud では App settings → Secrets に以下を設定します。

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "YOUR_SERVICE_ROLE_KEY"
SUPABASE_STORAGE_BUCKET = "visit-photos"
```

ローカルでは `.env.example` を `.env` にコピーして設定できます。`.env` は `.gitignore` 済みです。

## 3. 施設データを入れる

`data/facilities.csv` の列は次の通りです。

```text
id,name,category,ward,address,latitude,longitude,has_open_air_bath,has_natural_hot_spring,website_url,active,created_at,updated_at
```

`category` は `sento / super_sento / spa / other` のいずれかです。

本番利用では施設情報を Supabase `facilities` テーブルへ登録してください。CSV は初期データ作成・メンテナンス用の雛形として利用できます。

## 4. 起動

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## プロジェクト構成

```text
app.py
pages/
  home.py
  map.py
  facilities.py
  visit.py
  stampbook.py
services/
  supabase_service.py
  map_service.py
  stamp_service.py
components/
  facility_card.py
  stamp.py
assets/
  logo.png        # 正式ロゴをここへ配置
  tai_stamp.png   # 訪問スタンプ
data/
  facilities.csv
sql/
  001_schema.sql
requirements.txt
.env.example
README.md
```

## MVPの公開範囲

ログインなしのため、Streamlit アプリ自体は非公開・限定公開で運用してください。一般公開へ移行する場合は Supabase Auth とユーザー単位の RLS ポリシーを追加する前提の構造です。
