// JavaScript

/**
 * UWPアプリからBase64形式の画像データを受け取り、プレビュー表示を更新する関数
 * @param {string} base64ImageData - 'data:image/jpeg;base64,...' 形式の画像データ文字列
 */
function displayScannedImage(base64ImageData) {
  // HTMLから画像表示用の要素を取得
  const previewImage = document.getElementById('scanned-image-preview');
  const placeholderText = document.getElementById('placeholder-text');

  if (previewImage && placeholderText) {
    if (base64ImageData) {
      // 画像データがあれば、imgタグのsrcに設定し、プレースホルダーを隠す
      previewImage.src = base64ImageData;
      placeholderText.style.display = 'none';
      previewImage.style.display = 'block';
    } else {
      // 画像データがなければ、プレースホルダーを表示する
      previewImage.src = '';
      placeholderText.style.display = 'block';
      previewImage.style.display = 'none';
    }
  }
}

// ページの初期状態でプレースホルダーが表示されるように調整
document.addEventListener('DOMContentLoaded', () => {
    displayScannedImage(null);
});