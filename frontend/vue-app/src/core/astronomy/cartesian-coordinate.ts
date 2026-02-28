import * as THREE from 'three'

/**
 * 将赤道坐标 (RA, Dec) 转换为 3D 笛卡尔坐标
 * 与 astronomy 库定义的一致，X 指向春分点（RA = 0h, Dec = 0°），Y 指向 RA = 90度, Dec = 0度，Z 指向北天极（Dec = +90°）
 * @param ra 赤经 (度)
 * @param dec 赤纬 (度)
 * @param radius 半径，默认 1000
 */
export function raDecToVector3(ra: number, dec: number, radius: number = 1000): THREE.Vector3 {
  const radDec = THREE.MathUtils.degToRad(dec)
  const radRa = THREE.MathUtils.degToRad(ra)

  const cosDec = Math.cos(radDec)

  return new THREE.Vector3(
    radius * cosDec * Math.cos(radRa),
    radius * cosDec * Math.sin(radRa),
    radius * Math.sin(radDec),
  )
}
