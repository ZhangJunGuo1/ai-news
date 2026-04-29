const safeAdd = (x: number, y: number): number => {
  const lsw = (x & 0xffff) + (y & 0xffff);
  const msw = (x >>> 16) + (y >>> 16) + (lsw >>> 16);
  return ((msw & 0xffff) << 16) | (lsw & 0xffff);
};

const bitRotateLeft = (num: number, val: number): number => {
  return ((num << val) | (num >>> (32 - val))) >>> 0;
};

const md5FF = (a: number, b: number, c: number, d: number, x: number, s: number, t: number): number => {
  return safeAdd(bitRotateLeft(safeAdd(safeAdd(a, b & c ^ ~b & d), safeAdd(x, t)), s), b);
};

const md5GG = (a: number, b: number, c: number, d: number, x: number, s: number, t: number): number => {
  return safeAdd(bitRotateLeft(safeAdd(safeAdd(a, b & d ^ c & ~d), safeAdd(x, t)), s), b);
};

const md5HH = (a: number, b: number, c: number, d: number, x: number, s: number, t: number): number => {
  return safeAdd(bitRotateLeft(safeAdd(safeAdd(a, b ^ c ^ d), safeAdd(x, t)), s), b);
};

const md5II = (a: number, b: number, c: number, d: number, x: number, s: number, t: number): number => {
  return safeAdd(bitRotateLeft(safeAdd(safeAdd(a, c ^ (b | ~d)), safeAdd(x, t)), s), b);
};

const binl2hex = (binarray: number[]): string => {
  const hexTab = '0123456789abcdef';
  let str = '';
  for (let i = 0; i < binarray.length * 4; i++) {
    const low = (binarray[i >> 2] >> ((i % 4) * 8)) & 0xff;
    str += hexTab.charAt((low >> 4) & 0xf) + hexTab.charAt(low & 0xf);
  }
  return str;
};

const str2binl = (str: string): number[] => {
  const bin: number[] = [];
  let mask = (1 << 8) - 1;
  for (let i = 0; i < str.length * 8; i += 8) {
    bin[i >> 5] |= (str.charCodeAt(i / 8) & mask) << (i % 32);
  }
  bin[str.length * 8 >> 5] |= 0x80 << (str.length * 8 % 32);
  bin[(((str.length * 8 + 64) >>> 9) << 4) + 14] = str.length * 8;
  return bin;
};

export const md5 = (str: string): string => {
  const x = str2binl(str);
  let a = 0x67452301;
  let b = 0xefcdab89;
  let c = 0x98badcfe;
  let d = 0x10325476;

  for (let i = 0; i < x.length; i += 16) {
    const olda = a;
    const oldb = b;
    const oldc = c;
    const oldd = d;

    a = md5FF(a, b, c, d, x[i], 7, 0xd76aa478);
    d = md5FF(d, a, b, c, x[i + 1], 12, 0xe8c7b756);
    c = md5FF(c, d, a, b, x[i + 2], 17, 0x242070db);
    b = md5FF(b, c, d, a, x[i + 3], 22, 0xc1bdceee);
    a = md5FF(a, b, c, d, x[i + 4], 7, 0xf57c0faf);
    d = md5FF(d, a, b, c, x[i + 5], 12, 0x4787c62a);
    c = md5FF(c, d, a, b, x[i + 6], 17, 0xa8304613);
    b = md5FF(b, c, d, a, x[i + 7], 22, 0xfd469501);
    a = md5FF(a, b, c, d, x[i + 8], 7, 0x698098d8);
    d = md5FF(d, a, b, c, x[i + 9], 12, 0x8b44f7af);
    c = md5FF(c, d, a, b, x[i + 10], 17, 0xffff5bb1);
    b = md5FF(b, c, d, a, x[i + 11], 22, 0x895cd7be);
    a = md5FF(a, b, c, d, x[i + 12], 7, 0x6b901122);
    d = md5FF(d, a, b, c, x[i + 13], 12, 0xfd987193);
    c = md5FF(c, d, a, b, x[i + 14], 17, 0xa679438e);
    b = md5FF(b, c, d, a, x[i + 15], 22, 0x49b40821);

    a = md5GG(a, b, c, d, x[i + 1], 5, 0xf61e2562);
    d = md5GG(d, a, b, c, x[i + 6], 9, 0xc040b340);
    c = md5GG(c, d, a, b, x[i + 11], 14, 0x265e5a51);
    b = md5GG(b, c, d, a, x[i], 20, 0xe9b6c7aa);
    a = md5GG(a, b, c, d, x[i + 5], 5, 0xd62f105d);
    d = md5GG(d, a, b, c, x[i + 10], 9, 0x02441453);
    c = md5GG(c, d, a, b, x[i + 15], 14, 0xd8a1e681);
    b = md5GG(b, c, d, a, x[i + 4], 20, 0xe7d3fbc8);
    a = md5GG(a, b, c, d, x[i + 9], 5, 0x21e1cde6);
    d = md5GG(d, a, b, c, x[i + 14], 9, 0xc33707d6);
    c = md5GG(c, d, a, b, x[i + 3], 14, 0xf4d50d87);
    b = md5GG(b, c, d, a, x[i + 8], 20, 0x455a14ed);
    a = md5GG(a, b, c, d, x[i + 13], 5, 0xa9e3e905);
    d = md5GG(d, a, b, c, x[i + 2], 9, 0xfcefa3f8);
    c = md5GG(c, d, a, b, x[i + 7], 14, 0x676f02d9);
    b = md5GG(b, c, d, a, x[i + 12], 20, 0x8d2a4c8a);

    a = md5HH(a, b, c, d, x[i + 5], 4, 0xfffa3942);
    d = md5HH(d, a, b, c, x[i + 8], 11, 0x8771f681);
    c = md5HH(c, d, a, b, x[i + 11], 16, 0x6d9d6122);
    b = md5HH(b, c, d, a, x[i + 14], 23, 0xfde5380c);
    a = md5HH(a, b, c, d, x[i + 1], 4, 0xa4beea44);
    d = md5HH(d, a, b, c, x[i + 4], 11, 0x4bdecfa9);
    c = md5HH(c, d, a, b, x[i + 7], 16, 0xf6bb4b60);
    b = md5HH(b, c, d, a, x[i + 10], 23, 0xbebfbc70);
    a = md5HH(a, b, c, d, x[i + 13], 4, 0x289b7ec6);
    d = md5HH(d, a, b, c, x[i], 11, 0xeaa127fa);
    c = md5HH(c, d, a, b, x[i + 3], 16, 0xd4ef3085);
    b = md5HH(b, c, d, a, x[i + 6], 23, 0x04881d05);
    a = md5HH(a, b, c, d, x[i + 9], 4, 0xd9d4d039);
    d = md5HH(d, a, b, c, x[i + 12], 11, 0xe6db99e5);
    c = md5HH(c, d, a, b, x[i + 15], 16, 0x1fa27cf8);
    b = md5HH(b, c, d, a, x[i + 2], 23, 0xc4ac5665);

    a = md5II(a, b, c, d, x[i], 6, 0xf4292244);
    d = md5II(d, a, b, c, x[i + 7], 10, 0x432aff97);
    c = md5II(c, d, a, b, x[i + 14], 15, 0xab9423a7);
    b = md5II(b, c, d, a, x[i + 5], 21, 0xfc93a039);
    a = md5II(a, b, c, d, x[i + 12], 6, 0x655b59c3);
    d = md5II(d, a, b, c, x[i + 3], 10, 0x8f0ccc92);
    c = md5II(c, d, a, b, x[i + 10], 15, 0xffeff47d);
    b = md5II(b, c, d, a, x[i + 1], 21, 0x85845dd1);
    a = md5II(a, b, c, d, x[i + 8], 6, 0x6fa87e4f);
    d = md5II(d, a, b, c, x[i + 15], 10, 0xfe2ce6e0);
    c = md5II(c, d, a, b, x[i + 6], 15, 0xa3014314);
    b = md5II(b, c, d, a, x[i + 13], 21, 0x4e0811a1);
    a = md5II(a, b, c, d, x[i + 4], 6, 0xf7537e82);
    d = md5II(d, a, b, c, x[i + 11], 10, 0xbd3af235);
    c = md5II(c, d, a, b, x[i + 2], 15, 0x2ad7d2bb);
    b = md5II(b, c, d, a, x[i + 9], 21, 0xeb86d391);

    a = safeAdd(a, olda);
    b = safeAdd(b, oldb);
    c = safeAdd(c, oldc);
    d = safeAdd(d, oldd);
  }

  return binl2hex([a, b, c, d]);
};