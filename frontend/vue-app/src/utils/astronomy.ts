import * as model from '../../../../gen/ts/models/index'
import * as astronomy from 'astronomy-engine'

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
  let gmst = 18.697374558 + 24.06570982441908 * D

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
  let ans: model.EquatorialCoordinate = {
    rightAscension: 0,
    declination: 0,
  }

  // Compute Local Sidereal Time (LST)
  let lst = getLST(timestamp, location.longitude)

  // Convert all units to radians
  let a = degreesToRadians(hc.altitude)
  let A = degreesToRadians(hc.azimuth)
  let phi = degreesToRadians(location.latitude)
  lst = (lst * Math.PI) / 12

  let delta = Math.asin(Math.sin(a) * Math.sin(phi) + Math.cos(a) * Math.cos(phi) * Math.cos(A))

  // Compute hour angle
  let x = (Math.sin(a) - Math.sin(phi) * Math.sin(delta)) / Math.cos(phi)
  let y = -Math.sin(A) * Math.cos(a)
  let hourAngle = Math.atan2(y, x)
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
  let ans: model.EquatorialCoordinate = {
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

export {
  convertHorizontalCoordinateToEquatorialCoordinate,
  convertHorizontalCoordinateToEquatorialCoordinatePro,
}
