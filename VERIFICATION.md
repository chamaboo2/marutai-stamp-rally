# 提出前確認

app.py 作成後、指示書と照合して以下を確認しました。

- [x] app.py はルーターと共通UIに限定し、巨大な単一ファイル化を回避
- [x] pages/home.py / map.py / facilities.py / visit.py / stampbook.py に画面分割
- [x] services/supabase_service.py / map_service.py / stamp_service.py に処理分割
- [x] Supabase SQL、Storage設計、Secrets前提を実装
- [x] OpenStreetMap + Folium + streamlit-folium を利用
- [x] 露天風呂、天然温泉、区、施設種類、訪問済み/未訪問フィルターを実装
- [x] カメラ撮影・写真選択の両方を実装
- [x] 元写真とスタンプ入り写真を別保存する処理を実装
- [x] 「○たい」+ 訪問日を右下へ合成
- [x] 同一施設の複数訪問を visits の別レコードとして保存
- [x] スタンプ帳の4種類の並べ替えを実装
- [x] 地図上で訪問済みを赤い「たい」マーカーに変更
- [x] 訪問施設数を「○湯」と表示
- [x] Supabase未設定でも画面確認できるデモモードを用意
- [x] 公式ロゴは勝手に再生成せず assets/logo.png の受け口を用意
- [x] Python構文チェックを全ファイルで実施
- [x] 写真スタンプ処理のテストを実施

未検証事項：この実行環境は外部ネットワークへ接続できないため、Streamlit / streamlit-folium / supabase パッケージを新規インストールして実サーバー起動する統合テストは実施できませんでした。requirements.txt は作成済みです。
