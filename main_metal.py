import cv2
import glob
import random

files = glob.glob("../originalphotos/metal/metal_good/*.png")

i = 1
e = 1

for file in files:
    image = cv2.imread(file)
    if image is None:
        continue

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.resize(gray, (512, 512))
    gray2 = cv2.medianBlur(gray2, 9)

    thresh2 = cv2.adaptiveThreshold(
        gray2, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        11, 1
    )

    b = 60
    mean_clean = thresh2.copy()
    mean_clean[:, :b] = 255
    mean_clean[:, -b:] = 255
    mean_clean[:b, :] = 255
    mean_clean[-b:, :] = 255

    inv = cv2.bitwise_not(mean_clean)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    inv = cv2.morphologyEx(inv, cv2.MORPH_CLOSE, kernel, iterations=1)

    contours, _ = cv2.findContours(inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    c = max(contours, key=cv2.contourArea)
    M = cv2.moments(c)

    cx_512 = int(M["m10"] / M["m00"])
    cy_512 = int(M["m01"] / M["m00"])

    (_, _), r_512 = cv2.minEnclosingCircle(c)
    r_512 = float(r_512)

    h0, w0 = gray.shape[:2]
    sx = w0 / 512.0
    sy = h0 / 512.0

    cx = int(cx_512 * sx)
    cy = int(cy_512 * sy)

    r = int(r_512 * (sx + sy) / 3)
    margin = int(r * 0.4)
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
        bg_color = image[0, 0].tolist()
        image_pad = cv2.copyMakeBorder(
            image, top, bottom, left, right,
            cv2.BORDER_REFLECT
        )
    else:
        image_pad = image

    x1 += left; x2 += left
    y1 += top;  y2 += top

    crop = image_pad[y1:y2, x1:x2]

    result = cv2.resize(crop, (512, 512))

    angle = random.uniform(20, 300)

    h, w = result.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    result = cv2.warpAffine(
        result,
        M,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE
    )

    vis = cv2.cvtColor(mean_clean, cv2.COLOR_GRAY2BGR)
    cv2.circle(vis, (cx_512, cy_512), 3, (0, 0, 255), -1)
    cv2.circle(vis, (cx_512, cy_512), int(r_512), (255, 0, 255), 1)
    cv2.drawContours(vis, [c], -1, (0, 255, 0), 1)


    if e == 3:
        e = 1

    out = f"../augmentationphotos/metal_aug/metal_good_aug/metal_good_RPi_CM3_{i}.png"
    cv2.imwrite(out, result)

    out2 = f"../augmentationphotos/metal_aug/metal_good_aug/metal_good_RPi_CM3_{i}_augment_{e}.png"
    blurred = cv2.GaussianBlur(result, (5, 5), 0)

    angle = random.uniform(20, 300)

    h, w = result.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    blurred = cv2.warpAffine(
        blurred,
        M,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE
    )
    cv2.imwrite(out2, blurred)

    e += 1
    out3 = f"../augmentationphotos/metal_aug/metal_good_aug/metal_good_RPi_CM3_{i}_augment_{e}.png"
    darker = cv2.convertScaleAbs(result, alpha=1.0, beta=-30)

    angle = random.uniform(20, 300)

    h, w = result.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    darker = cv2.warpAffine(
        darker,
        M,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE
    )
    cv2.imwrite(out3, darker)

    e += 1
    out4 = f"../augmentationphotos/metal_aug/metal_good_aug/metal_good_RPi_CM3_{i}_augment_{e}.png"
    brighter = cv2.convertScaleAbs(result, alpha=1.0, beta=30)

    angle = random.uniform(20, 300)

    h, w = result.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    brighter = cv2.warpAffine(
        brighter,
        M,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE
    )
    cv2.imwrite(out4, brighter)

    i += 1

    #cv2.imshow("result",result)
    #cv2.imshow("result", brighter)
    #cv2.imshow("result", darker)
    #cv2.imshow("result", blurred)
    #cv2.waitKey(0)

#cv2.destroyAllWindows()