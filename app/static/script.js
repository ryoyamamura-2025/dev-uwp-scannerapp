// JavaScript

/**
 * UWPアプリからBase64形式の画像データを受け取り、プレビュー表示を更新する関数
 * @param {string} base64ImageData - 'data:image/jpeg;base64,...' 形式の画像データ文字列
 */
async function displayScannedImage(base64ImageData) {
    // HTMLから画像表示用の要素を取得
    const previewImage = document.getElementById('scanned-image-preview');
    const placeholderText = document.getElementById('scan-placeholder-text');
    const psImage = document.getElementById('ps-image-preview');
    const psplaceholderText = document.getElementById('ps-placeholder-text');
      
    if (previewImage && placeholderText) {
      if (base64ImageData) {
          // 画像データがあれば、imgタグのsrcに設定し、プレースホルダーを隠す
          previewImage.src = base64ImageData;
          placeholderText.style.display = 'none';
          previewImage.style.display = 'block';
          
          try {
              const response = await fetch('/generate-image', {
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/json',
                  },
                  // Python側で定義した "image_data" というキーでデータを送信
                  body: JSON.stringify({ image_data: base64ImageData }),
              });

              // --- サーバーからのレスポンスを確認 ---
              if (!response.ok) {
              // HTTPステータスが200番台でない場合はエラー
                throw new Error(`サーバーエラーが発生しました: ${response.status}`);
              }
                
              const result = await response.json();

              if (result.error) {
              // FastAPI側でエラーが返された場合
                throw new Error(result.error);
              }

              // 画像データがあれば、imgタグのsrcに設定し、プレースホルダーを隠す
              psImage.src = result.image_data;
              psplaceholderText.style.display = 'none';
              psImage.style.display = 'block';

          } catch (error) {
              console.error('画像処理に失敗しました:', error);
              psplaceholderText.textContent = `エラー: ${error.message}`;
              psplaceholderText.style.display = 'block';
              psImage.style.display = 'none';
          }

      } else {
        // 画像データがなければ、プレースホルダーを表示する
        previewImage.src = '';
        placeholderText.style.display = 'block';
        previewImage.style.display = 'none';
        psImage.src = '';
        psplaceholderText.style.display = 'block';
        psImage.style.display = 'none';
      }
  }
}

// ページの初期状態でプレースホルダーが表示されるように調整
document.addEventListener('DOMContentLoaded', () => {
    const uploadInput = document.getElementById('image-upload-input');

    // ファイルが選択されたときの処理
    uploadInput.addEventListener('change', (event) => {
        const files = event.target.files;
        if (files && files[0]) {
            const file = files[0];
            const reader = new FileReader();

            // FileReaderでファイルの読み込みが完了したら実行
            reader.onload = (e) => {
                // 読み込んだ結果 (Base64文字列) を displayScannedImage 関数に渡す
                displayScannedImage(e.target.result);
            };

            // ファイルをData URL (Base64) として読み込む
            reader.readAsDataURL(file);
        }
    });
    displayScannedImage(null);
});