from services.vision_service import analyze_equipment_image

image_path = "test_images/breaker.jpeg"

result = analyze_equipment_image(image_path)

print("\nIMAGE ANALYSIS:\n")
print(result)