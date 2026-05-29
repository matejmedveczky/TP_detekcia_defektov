import cv2
import glob
import numpy as np

def fill_border(img, color, b=4):
    img[:b, :] = color
    img[-b:, :] = color
    img[:, :b] = color
    img[:, -b:] = color
    return img

files = glob.glob("../originalphotos/depthmap/depth_good/*.png")

i = 1
e = 1

for file in files:
    image = cv2.imread(file)
    if image is None:
        continue

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 7)

    _, mask = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    kernel = np.ones((3, 3), np.uint8)

    mask = cv2.dilate(mask, kernel, iterations=10)
    #mask = cv2.bitwise_not(mask)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        mask, 4, cv2.CV_32S
    )

    vis = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    obj_idx = 1

    for label in range(1, num_labels):
        area = stats[label, cv2.CC_STAT_AREA]

        if area < 2000:
            continue

        x = stats[label, cv2.CC_STAT_LEFT]
        y = stats[label, cv2.CC_STAT_TOP]
        w_box = stats[label, cv2.CC_STAT_WIDTH]
        h_box = stats[label, cv2.CC_STAT_HEIGHT]

        cx = int(centroids[label][0])
        cy = int(centroids[label][1])

        r = int(max(w_box, h_box) / 2)
        margin = int(r * 0.7)
        half = r + margin

        x1 = cx - half
        y1 = cy - half
        x2 = cx + half
        y2 = cy + half

        top = max(0, -y1)
        left = max(0, -x1)
        bottom = max(0, y2 - image.shape[0])
        right = max(0, x2 - image.shape[1])

        if top or left or bottom or right:
            image_pad = cv2.copyMakeBorder(
                image, top, bottom, left, right,
                cv2.BORDER_REFLECT
            )
            labels_pad = cv2.copyMakeBorder(
                labels, top, bottom, left, right,
                cv2.BORDER_CONSTANT, value=0
            )
        else:
            image_pad = image
            labels_pad = labels

        x1 += left
        x2 += left
        y1 += top
        y2 += top

        crop = image_pad[y1:y2, x1:x2].copy()
        crop_labels = labels_pad[y1:y2, x1:x2]

        component_mask = (crop_labels == label).astype(np.uint8) * 255
        component_mask = cv2.GaussianBlur(component_mask, (7, 7), 0)

        alpha = component_mask.astype(np.float32) / 255.0
        alpha = cv2.merge([alpha, alpha, alpha])

        corners = np.vstack([
            crop[:20, :20].reshape(-1, 3),
            crop[:20, -20:].reshape(-1, 3),
            crop[-20:, :20].reshape(-1, 3),
            crop[-20:, -20:].reshape(-1, 3)
        ])
        bg_color = np.median(corners, axis=0).astype(np.uint8)

        bg_img = np.full_like(crop, bg_color)

        clean_crop = (
            crop.astype(np.float32) * alpha +
            bg_img.astype(np.float32) * (1.0 - alpha)
        ).astype(np.uint8)

        result = cv2.resize(clean_crop, (512, 512), interpolation=cv2.INTER_LINEAR)
        result = fill_border(result, bg_color, 4)

        cv2.rectangle(vis, (x, y), (x + w_box, y + h_box), (255, 0, 0), 1)
        cv2.circle(vis, (cx, cy), 3, (0, 0, 255), -1)

        out1 = f"../augmentationphotos/depth_aug/depth_good_aug/depth_good_RPi_CM3_{i}.png"
        cv2.imwrite(out1, result)

        obj_idx += 1
        i += 1

    # cv2.imshow("result",result)
    # cv2.imshow("result", result_rot)
    # cv2.imshow("result", result_zoomout)
    # cv2.imshow("result", result_zoomin)
    # cv2.waitKey(0)

# cv2.destroyAllWindows()