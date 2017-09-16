画像読み込みについて

javaを使うと以下のように各ピクセルの値が取得できます。

// image file path
String imgFilePath = "img/large.png";
File imgFile = new File(imgFilePath);
// read image
BufferedImage img = ImageIO.read(imgFile);
// width and height
int w = img.getWidth(), h = img.getHeight();
// get pixels
int[] pixels = img.getData().getPixels(0, 0, w, h, new int[w*h]);

ちなみに、添付のlarge.pngの左上(0,0)の値は61になります。