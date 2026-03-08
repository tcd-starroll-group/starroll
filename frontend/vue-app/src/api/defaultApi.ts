import { DefaultApi } from '../../../../gen/ts/apis/DefaultApi'
import { Configuration } from '../../../../gen/ts/runtime'

const configuration = new Configuration({
  basePath: '',
  middleware: [
    {
      pre: async ({ url, init }) => {
        const token = localStorage.getItem('token')
        const headers = new Headers(init.headers)

        if (token) {
          headers.set('Authorization', `Bearer ${token}`)
        }

        return {
          url,
          init: {
            ...init,
            headers,
          },
        }
      },
    },
  ],
})

export const defaultApi = new DefaultApi(configuration)
