import { expect, test, describe } from 'vitest'
import * as astronomy from './astronomy'
import * as model from '../../../../gen/ts/models/index'

describe('convertHorizontalCoordinateToEquatorialCoordinate', () => {
  test('should return similar results for both methods', () => {
    const cases: Array<{
      name: string
      hc: model.HorizontalCoordinate
      timestamp: number
      location: model.GPS
    }> = [
      {
        name: 'NYC spring equinox dawn',
        hc: { altitude: 20, azimuth: 90 },
        timestamp: Date.UTC(2024, 2, 20, 9, 0, 0),
        location: { latitude: 40.7128, longitude: -74.006 },
      },
      {
        name: 'SF summer evening',
        hc: { altitude: 45, azimuth: 220 },
        timestamp: Date.UTC(2024, 6, 1, 3, 0, 0),
        location: { latitude: 37.7749, longitude: -122.4194 },
      },
      {
        name: 'Sydney winter night',
        hc: { altitude: 60, azimuth: 150 },
        timestamp: Date.UTC(2024, 5, 15, 12, 0, 0),
        location: { latitude: -33.8688, longitude: 151.2093 },
      },
      {
        name: 'London autumn morning',
        hc: { altitude: 30, azimuth: 45 },
        timestamp: Date.UTC(2024, 9, 10, 6, 30, 0),
        location: { latitude: 51.5074, longitude: -0.1278 },
      },
    ]

    cases.forEach(({ name, hc, timestamp, location }) => {
      const result1 = astronomy.convertHorizontalCoordinateToEquatorialCoordinate(
        hc,
        timestamp,
        location,
      )
      console.log(`[${name}] my result:`, result1)

      const result2 = astronomy.convertHorizontalCoordinateToEquatorialCoordinatePro(
        hc,
        timestamp,
        location,
      )
      console.log(`[${name}] pro result:`, result2)

      expect(Math.abs(result1.rightAscension - result2.rightAscension)).toBeLessThan(1)
      expect(Math.abs(result1.declination - result2.declination)).toBeLessThan(1)
    })
  })
})

describe('convertEquatorialCoordinateToCartesianCoordinate', () => {
  test('should convert equatorial to cartesian correctly', () => {
    const cases: Array<{
      name: string
      ec: model.EquatorialCoordinate
      radius: number
    }> = [
      {
        name: 'RA=0°, Dec=0° (X轴)',
        ec: { rightAscension: 0, declination: 0 },
        radius: 100,
      },
      {
        name: 'RA=90°, Dec=0° (Y轴)',
        ec: { rightAscension: 90, declination: 0 },
        radius: 100,
      },
      {
        name: 'RA=0°, Dec=90° (Z轴)',
        ec: { rightAscension: 0, declination: 90 },
        radius: 100,
      },
      {
        name: '织女星 (Vega)',
        ec: { rightAscension: 279.23, declination: 38.78 },
        radius: 100,
      },
      {
        name: '天狼星 (Sirius)',
        ec: { rightAscension: 101.29, declination: -16.72 },
        radius: 100,
      },
    ]

    cases.forEach(({ name, ec, radius }) => {
      const result = astronomy.convertEquatorialCoordinateToCartesianCoordinate(ec, radius)
      console.log(`[${name}]`, result)

      const distance = Math.sqrt(result.x ** 2 + result.y ** 2 + result.z ** 2)
      expect(distance).toBeCloseTo(radius, 1)
    })
  })

  test('should return similar results for both methods', () => {
    const cases: Array<{
      name: string
      ec: model.EquatorialCoordinate
      timestamp: number
      radius: number
    }> = [
      {
        name: '赤道点（Equator）',
        ec: { rightAscension: 0, declination: 0 },
        timestamp: Date.UTC(2024, 0, 1, 0, 0, 0),
        radius: 100,
      },
      {
        name: '北极星（Polaris）',
        ec: { rightAscension: 37.95, declination: 89.26 },
        timestamp: Date.UTC(2024, 6, 1, 12, 0, 0),
        radius: 100,
      },
      {
        name: '织女星（Vega）',
        ec: { rightAscension: 279.23, declination: 38.78 },
        timestamp: Date.UTC(2024, 6, 15, 20, 0, 0),
        radius: 100,
      },
    ]

    cases.forEach(({ name, ec, timestamp, radius }) => {
      const result1 = astronomy.convertEquatorialCoordinateToCartesianCoordinate(ec, radius)
      console.log(`[${name}] basic result:`, result1)

      const result2 = astronomy.convertEquatorialCoordinateToCartesianCoordinatePro(
        ec,
        timestamp,
        radius,
      )
      console.log(`[${name}] pro result:`, result2)

      expect(Math.abs(result1.x - result2.x)).toBeLessThan(radius * 0.1)
      expect(Math.abs(result1.y - result2.y)).toBeLessThan(radius * 0.1)
      expect(Math.abs(result1.z - result2.z)).toBeLessThan(radius * 0.1)
    })
  })

  test('should batch convert correctly', () => {
    const stars: model.EquatorialCoordinate[] = [
      { rightAscension: 0, declination: 0 },
      { rightAscension: 90, declination: 0 },
      { rightAscension: 0, declination: 90 },
      { rightAscension: 279.23, declination: 38.78 },
    ]

    const radius = 100
    const results = astronomy.batchConvertEquatorialToCartesian(stars, radius)

    expect(results.length).toBe(stars.length)

    results.forEach((result, index) => {
      const distance = Math.sqrt(result.x ** 2 + result.y ** 2 + result.z ** 2)
      expect(distance).toBeCloseTo(radius, 1)
      console.log(`Star ${index}:`, result)
    })
  })
})
