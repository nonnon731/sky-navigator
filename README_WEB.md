# ANA SKY NAVIGATOR - Web版デプロイメントガイド

## 🌐 ブラウザ版について

PygameゲームをWebブラウザで動作させるためのファイルを作成しました。

## 📁 ファイル構成

```
/home/nonno/
├── airplane_game_web.py  # Web版ゲームコード（asyncio対応）
├── index.html           # HTMLファイル
└── README_WEB.md       # このファイル
```

## 🚀 デプロイ方法

### 方法1: GitHub Pages（推奨）

1. **GitHubリポジトリを作成**
   ```bash
   git init
   git add airplane_game_web.py index.html
   git commit -m "Add ANA Sky Navigator Web Game"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/ana-sky-navigator.git
   git push -u origin main
   ```

2. **GitHub Pagesを有効化**
   - リポジトリの Settings → Pages
   - Source: Deploy from a branch
   - Branch: main / (root)
   - Save

3. **アクセス**
   - `https://YOUR_USERNAME.github.io/ana-sky-navigator/`

### 方法2: Netlify

1. **Netlifyにファイルをアップロード**
   - [netlify.com](https://netlify.com) にアクセス
   - "Deploy manually" でファイルをドラッグ&ドロップ

2. **自動デプロイ**
   - 自動的にURLが生成されます

### 方法3: Vercel

1. **Vercelにデプロイ**
   ```bash
   npx vercel --prod
   ```

## ⚠️ 重要な注意事項

### 現在の制限事項

1. **Pyodide/Pygame-Web の制限**
   - 完全なPygameサポートはまだ実験的段階
   - 一部の機能が動作しない可能性があります

2. **パフォーマンス**
   - ネイティブ版より動作が重い場合があります
   - モバイルデバイスでは特に注意が必要

3. **ブラウザ互換性**
   - モダンブラウザ（Chrome, Firefox, Safari, Edge）推奨
   - WebAssembly対応が必要

## 🔧 代替案: Pygame-Web (Pygbag)

より確実な方法として、Pygbagを使用することをお勧めします：

### Pygbagのインストールと使用

```bash
# Pygbagをインストール
pip install pygbag

# ゲームをWeb用にビルド
pygbag airplane_game_web.py
```

### Pygbag用のコード修正

```python
# airplane_game_web.py の最後を以下に変更
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## 🌟 推奨デプロイ手順

1. **Pygbagを使用してビルド**
   ```bash
   pip install pygbag
   pygbag airplane_game_web.py --width 800 --height 600 --name "ANA Sky Navigator"
   ```

2. **生成されたファイルをホスティング**
   - `dist/` フォルダの内容をWebサーバーにアップロード

3. **URL例**
   - `https://your-domain.com/ana-sky-navigator/`

## 🎮 Web版の特徴

- **軽量化**: ファイルサイズを最適化
- **シンプルUI**: Web環境に適したインターフェース
- **レスポンシブ**: 様々な画面サイズに対応
- **セッション管理**: ブラウザセッション内でのスコア管理

## 📱 モバイル対応

現在のバージョンはキーボード操作のみですが、将来的にタッチ操作にも対応予定です。

## 🔗 参考リンク

- [Pygame-Web (Pygbag)](https://github.com/pygame-web/pygbag)
- [Pyodide](https://pyodide.org/)
- [GitHub Pages](https://pages.github.com/)
- [Netlify](https://netlify.com/)
