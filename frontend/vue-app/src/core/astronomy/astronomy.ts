import * as model from '../../../../../gen/ts/models/index'
import * as astronomy from 'astronomy-engine'
import * as THREE from 'three'

function degreesToRadians(degrees: number): number {
  return (degrees * Math.PI) / 180
}

function radiansToDegrees(radians: number): number {
  return (radians * 180) / Math.PI
}

function getLST(timestamp: number, longitude: number): number {
  // 1. Compute Julian Date (JD)
  const jd = timestamp / 86400000 + 2440587.5
  const D = jd - 2451545.0

  // 2. Compute Greenwich Mean Sidereal Time (GMST)
  const gmst = 18.697374558 + 24.06570982441908 * D

  // 3. Apply longitude correction (1 degree = 1/15 hour)
  let lst = gmst + longitude / 15.0

  // 4. Normalize to 0-24 hours
  lst = lst % 24
  if (lst < 0) lst += 24

  return lst
}

// Converts horizontal coordinates (azimuth, altitude) in degrees to equatorial coordinates (RA, Dec) in degrees,
// using a UTC timestamp (milliseconds since epoch) and an observer location (latitude, longitude) in degrees.
function convertHorizontalCoordinateToEquatorialCoordinate(
  hc: model.HorizontalCoordinate,
  timestamp: number,
  location: model.GPS,
): model.EquatorialCoordinate {
  const ans: model.EquatorialCoordinate = {
    rightAscension: 0,
    declination: 0,
  }

  // Compute Local Sidereal Time (LST)
  let lst = getLST(timestamp, location.longitude)

  // Convert all units to radians
  const a = degreesToRadians(hc.altitude)
  const A = degreesToRadians(hc.azimuth)
  const phi = degreesToRadians(location.latitude)
  lst = (lst * Math.PI) / 12

  const delta = Math.asin(Math.sin(a) * Math.sin(phi) + Math.cos(a) * Math.cos(phi) * Math.cos(A))

  // Compute hour angle
  const x = (Math.sin(a) - Math.sin(phi) * Math.sin(delta)) / Math.cos(phi)
  const y = -Math.sin(A) * Math.cos(a)
  const hourAngle = Math.atan2(y, x)
  let alpha = lst - hourAngle
  // Normalize to [0, 2PI)
  alpha = alpha % (2 * Math.PI)
  if (alpha < 0) {
    alpha += 2 * Math.PI
  }
  // Convert to degrees
  ans.rightAscension = radiansToDegrees(alpha)
  ans.declination = radiansToDegrees(delta)
  return ans
}

// Same conversion but using the professional library.
// Altitude defaults to 0; provide actual altitude for higher accuracy.
function convertHorizontalCoordinateToEquatorialCoordinatePro(
  hc: model.HorizontalCoordinate,
  timestamp: number,
  location: model.GPS,
): model.EquatorialCoordinate {
  const ans: model.EquatorialCoordinate = {
    rightAscension: 0,
    declination: 0,
  }
  const time = new astronomy.AstroTime(new Date(timestamp))
  const observer = new astronomy.Observer(location.latitude, location.longitude, 0)

  const horizontalVector = astronomy.VectorFromHorizon(
    new astronomy.Spherical(hc.altitude, hc.azimuth, 1),
    time,
    'normal',
  )

  // Rotation_HOR_EQJ: horizon -> J2000 mean equatorial (catalog use)
  // Rotation_HOR_EQD: horizon -> true equatorial of date (current positions)
  const rotationMatrix = astronomy.Rotation_HOR_EQD(time, observer)
  const equatorialVector = astronomy.RotateVector(rotationMatrix, horizontalVector)
  const equator = astronomy.EquatorFromVector(equatorialVector)

  ans.rightAscension = equator.ra * 15 // 小时转度
  ans.declination = equator.dec
  return ans
}

function convertHorizontalQuaternionToEquatorialQuaternionPro(
  horizontalQuaternion: [number, number, number, number],
  timestamp: number,
  location: model.GPS,
): [number, number, number, number] {
  const time = new astronomy.AstroTime(new Date(timestamp))
  const observer = new astronomy.Observer(location.latitude, location.longitude, 0)

  // 1. 获取 HOR -> EQD 旋转矩阵 (通常 astronomy 返回 3x3 行优先矩阵)
  const rotationMatrix = astronomy.Rotation_HOR_EQD(time, observer)
  const m = rotationMatrix.rot

  const frameRotationMatrix = new THREE.Matrix4()

  frameRotationMatrix
    .set(
      m[0][0],
      m[0][1],
      m[0][2],
      0,
      m[1][0],
      m[1][1],
      m[1][2],
      0,
      m[2][0],
      m[2][1],
      m[2][2],
      0,
      0,
      0,
      0,
      1,
    )
    .transpose() // 重要：将行优先转为 THREE.js 的列优先

  const qH2E_astro = new THREE.Quaternion().setFromRotationMatrix(frameRotationMatrix)

  // 手机的坐标系是 E-N-U 到 astronomy 的 坐标系 N-W-U 需绕 Z -90度
  const qUserToAstro = new THREE.Quaternion().setFromAxisAngle(
    new THREE.Vector3(0, 0, 1),
    -Math.PI / 2,
  )

  // const qAstroToUser = qUserToAstro.clone().invert()

  // 3. 原始输入四元数 (确保顺序是 [x, y, z, w])
  const sourceQuaternion = new THREE.Quaternion(
    horizontalQuaternion[0],
    horizontalQuaternion[1],
    horizontalQuaternion[2],
    horizontalQuaternion[3],
  ).normalize()

  /**
   * 4. 组合变换
   * 逻辑：先将姿态转到天文空间 -> 应用地平到赤道的旋转
   * 矩阵顺序：Target = Q_A2U * Q_H2E * Q_U2A * Source
   */
  const targetQuaternion = new THREE.Quaternion()
    // .copy(qAstroToUser)
    .multiply(qH2E_astro)
    .multiply(qUserToAstro)
    .multiply(sourceQuaternion)
    .normalize()

  return [targetQuaternion.x, targetQuaternion.y, targetQuaternion.z, targetQuaternion.w]
}

/**
 * @param orientation [x, y, z, w] 形式的原始四元数数组
 * @returns 旋转后的 [x, y, z, w] 数组
 */
function offsetRoll(
  orientation: [number, number, number, number],
): [number, number, number, number] {
  // 1. 初始化 Three.js 四元数对象
  const q = new THREE.Quaternion().fromArray(orientation)

  const deltaY = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI / 2)

  q.multiply(deltaY)

  // 返回数组格式 [x, y, z, w]
  return q.toArray() as [number, number, number, number]
}

export {
  offsetRoll,
  convertHorizontalCoordinateToEquatorialCoordinate,
  convertHorizontalCoordinateToEquatorialCoordinatePro,
  convertHorizontalQuaternionToEquatorialQuaternionPro,
}
