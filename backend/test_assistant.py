from backend.services.assistant_service import generate_assistant_response

image_path = "test_images/breaker.jpeg"

query = "What should I do if this electrical panel overheats?"

response = generate_assistant_response(image_path, query)

print(response)