import os.path as osp
import cv2
import numpy as np
import torch
import RRDBNet_arch as arch

# Load the model once when the application starts
MODEL_PATH = 'models/RRDB_ESRGAN_x4.pth'
DEVICE = torch.device('cpu')#'cuda' if torch.cuda.is_available() else
MODEL = arch.RRDBNet(3, 3, 64, 23, gc=32).to(DEVICE)
MODEL.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE), strict=True)
MODEL.eval()

def enhance_image(image_path):
    try:
        base = osp.splitext(osp.basename(image_path))[0]
        print('Enhancing image:', base)
        
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            print(f"Error: Unable to read image at {image_path}")
            return None

        # Preprocess the image
        img = img * 1.0 / 255
        img = torch.from_numpy(np.transpose(img[:, :, [2, 1, 0]], (2, 0, 1))).float()
        img_LR = img.unsqueeze(0).to(DEVICE)

        # Enhance the image
        with torch.no_grad():
            output = MODEL(img_LR).squeeze().float().clamp_(0, 1).cpu().numpy()
        output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0)) * 255.0
        output = output.round().astype(np.uint8)

        # Save the enhanced image
        enhanced_image_path = f'results/{base}_enhanced.png'
        cv2.imwrite(enhanced_image_path, output)

        return enhanced_image_path

    except Exception as e:
        print(f"Error enhancing image {osp.basename(image_path)}: {e}")
        return None
