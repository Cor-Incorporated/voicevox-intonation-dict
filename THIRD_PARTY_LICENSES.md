# Third Party Licenses

本リポジトリは以下のオープンソースソフトウェアに依存しています。

## VOICEVOX関連

- **VOICEVOX**
  - URL: <https://voicevox.hiroshiba.jp/>
  - 用途: 音声合成エンジン本体
  - ライセンス: 参照用ソース内の `LICENSE` によると、LGPL v3 と
    ソースコード公開不要の別ライセンスのデュアルライセンス
  - 備考: 本リポジトリはVOICEVOX Engineを改変せず、HTTP APIを利用する
    拡張辞書中間サーバーです。

## 直接依存

`server/requirements.txt` で確認できる直接依存は以下です。

- **fastapi** (`>=0.109.0`) - Web API フレームワーク、MIT License
- **uvicorn[standard]** (`>=0.27.0`) - ASGI サーバー、BSD-3-Clause
- **httpx** (`>=0.26.0`) - HTTP クライアント、BSD-3-Clause
- **pydantic** (`>=2.5.0`) - データバリデーション、MIT License
- **pydantic-settings** (`>=2.0.0`) - 設定管理、配布時に要確認
- **python-dotenv** (`>=1.0.0`) - `.env` 読み込み、BSD-3-Clause

各依存パッケージの正確なライセンス条件は、配布時にインストールされる
各パッケージのメタデータおよび上流リポジトリを確認してください。

## 参照用ソース

`reference/voicevox_engine/` は開発時参照用のVOICEVOX Engineソースであり、
親リポジトリでは `.gitignore` により管理対象外です。参照用ソースの
ライセンスは同ディレクトリ内の `LICENSE` および関連ライセンスファイルを
確認してください。

## 重要事項

これらのOSSは、本リポジトリ作成以前から公開・利用可能な公知の
ソフトウェアです。

本リポジトリ自体はCor.株式会社の独自実装であり、個別案件の秘密情報に
よらず独自に開発した情報として記録します。

VOICEVOX本体およびその他の依存OSSは、いかなる個別契約以前から公開されている
公知のソフトウェアです。
