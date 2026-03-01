class VisionModel:
    def analyze_image(self, image_bytes):
        size_bytes = len(image_bytes) if image_bytes else 0
        return {
            "analysis": "Image received for analysis.",
            "bytes": size_bytes,
        }
