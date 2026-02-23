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

    cases.forEach(({ hc, timestamp, location }) => {
      const result1 = astronomy.convertHorizontalCoordinateToEquatorialCoordinate(
        hc,
        timestamp,
        location,
      )
      // console.log(`[${name}] my result:`, result1)

      const result2 = astronomy.convertHorizontalCoordinateToEquatorialCoordinatePro(
        hc,
        timestamp,
        location,
      )
      // console.log(`[${name}] pro result:`, result2)

      expect(Math.abs(result1.rightAscension - result2.rightAscension)).toBeLessThan(1)
      expect(Math.abs(result1.declination - result2.declination)).toBeLessThan(1)
    })
  })
})
