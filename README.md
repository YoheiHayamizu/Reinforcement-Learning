# pydev

gitの使用について
---
* ブランチ名
`master`  -> リリース用ブランチ(リリース時以外更新しない)  
`develop` -> 開発用ブランチ
`feature/*` -> 機能実装用ブランチ
`hotfix/*` -> バグ修正用ブランチ(大規模バグの場合のみ)
featureとhotfix以外は, 適宜コミットメッセージのprefix(choreなど)を上位ディレクトリ名とすること．

* コミット  
コメントは基本的に英語で書く(端末上で日本語が文字化けして読めないことが多く, 緊急時にログが確認できないと困るため)．<br>  
コミット時のコメントにはprefixをつけて管理する.  
prefixの付け方は以下のサイトを参照.   
https://qiita.com/numanomanu/items/45dd285b286a1f7280ed  
  
  * **feat**: 新機能実装
  * **fix**: バグの修正
  * **docs**: ドキュメントのみの変更 
  * **style**: コード内のスタイルの変更（改行やフォーマットなどの機能以外の変更）
  * **refactor**: 修正や新機能以外のコードの修正
  * **perf**: 機能のパフォーマンス向上
  * **test**: 機能テストの追加
  * **chore**: Makefile,ライブラリ,その他の補足ツールの変更

* プルリクエスト  
プルリクエストのタイトルにも，コミットメッセージと同様のprefixを付ける．
