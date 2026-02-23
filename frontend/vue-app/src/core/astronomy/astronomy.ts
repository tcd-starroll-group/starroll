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
  // Rotation_HOR_EQJ: horizon -> J2000 mean equatorial (catalog use)
  // Rotation_HOR_EQD: horizon -> true equatorial of date (current positions)
  const rotationMatrix = astronomy.Rotation_HOR_EQD(time, observer)
  const matrix3 = rotationMatrix.rot
  const frameRotationMatrix = new THREE.Matrix4().set(
    matrix3[0][0],
    matrix3[0][1],
    matrix3[0][2],
    0,
    matrix3[1][0],
    matrix3[1][1],
    matrix3[1][2],
    0,
    matrix3[2][0],
    matrix3[2][1],
    matrix3[2][2],
    0,
    0,
    0,
    0,
    1,
  )

  const rotationQuaternion = new THREE.Quaternion()
    .setFromRotationMatrix(frameRotationMatrix)
    .normalize()
  const sourceQuaternion = new THREE.Quaternion(
    horizontalQuaternion[0],
    horizontalQuaternion[1],
    horizontalQuaternion[2],
    horizontalQuaternion[3],
  ).normalize()

  const targetQuaternion = rotationQuaternion.multiply(sourceQuaternion).normalize()
  return [targetQuaternion.x, targetQuaternion.y, targetQuaternion.z, targetQuaternion.w]
}

export {
  convertHorizontalCoordinateToEquatorialCoordinate,
  convertHorizontalCoordinateToEquatorialCoordinatePro,
  convertHorizontalQuaternionToEquatorialQuaternionPro,
}
