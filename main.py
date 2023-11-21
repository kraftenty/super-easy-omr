import preprocess
import detect

preprocessedImg = preprocess.getProcessedImage()
detectedValues = detect.getDetectedValues(preprocessedImg)

print(detectedValues)
