function a = computeconvex(pyarr)
    matarr = bwconvhull(pyarr);
    a = sum(matarr(:))
