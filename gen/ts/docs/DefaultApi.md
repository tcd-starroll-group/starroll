# DefaultApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**apiCalculateStarCoordinatesPost**](DefaultApi.md#apicalculatestarcoordinatespostoperation) | **POST** /api/calculateStarCoordinates | calculate star coordinates |
| [**apiChangePasswordPost**](DefaultApi.md#apichangepasswordpost) | **POST** /api/changePassword |  |
| [**apiCheckRoomStatusPost**](DefaultApi.md#apicheckroomstatuspostoperation) | **POST** /api/checkRoomStatus | Check chat room status |
| [**apiCommentBlogPost**](DefaultApi.md#apicommentblogpostoperation) | **POST** /api/commentBlog | Comment a blog |
| [**apiCreateBlogPost**](DefaultApi.md#apicreateblogpostoperation) | **POST** /api/createBlog | Create a new blog |
| [**apiCreateIdentifyStarsJobPost**](DefaultApi.md#apicreateidentifystarsjobpost) | **POST** /api/createIdentifyStarsJob | Create a job to identify the stars in the image. |
| [**apiDeleteBlogPost**](DefaultApi.md#apideleteblogpost) | **POST** /api/deleteBlog | Delete a blog |
| [**apiDeleteCommentPost**](DefaultApi.md#apideletecommentpostoperation) | **POST** /api/deleteComment | Delete a comment |
| [**apiDeleteUserPost**](DefaultApi.md#apideleteuserpost) | **POST** /api/deleteUser | 注销账号 |
| [**apiDisplayChatRoomGet**](DefaultApi.md#apidisplaychatroomget) | **GET** /api/displayChatRoom | Display chat room entry button in GUI |
| [**apiDisplaySaveSuccessPost**](DefaultApi.md#apidisplaysavesuccesspostoperation) | **POST** /api/displaySaveSuccess | Display save success confirmation |
| [**apiDisplayStarDetailsPost**](DefaultApi.md#apidisplaystardetailspostoperation) | **POST** /api/displayStarDetails | Display star details |
| [**apiDisplayStarfieldPost**](DefaultApi.md#apidisplaystarfieldpostoperation) | **POST** /api/displayStarfield | Display starfield |
| [**apiElimilateErrorsPost**](DefaultApi.md#apielimilateerrorspostoperation) | **POST** /api/elimilateErrors | Eliminating the errors between the stars\&#39; positions that we calculated and the stars\&#39; positions captured by the camera. These errors are generally caused by the limited accuracy of the sensor. |
| [**apiExitChatRoomPost**](DefaultApi.md#apiexitchatroompostoperation) | **POST** /api/exitChatRoom | Exit chat room |
| [**apiGetAttitudePost**](DefaultApi.md#apigetattitudepost) | **POST** /api/getAttitude | Get attitude of the mobile device |
| [**apiGetCameraDataPost**](DefaultApi.md#apigetcameradatapost) | **POST** /api/getCameraData | Get camera data |
| [**apiGetChatRoomInfoPost**](DefaultApi.md#apigetchatroominfopostoperation) | **POST** /api/getChatRoomInfo | Retrieve chat room from social system |
| [**apiGetChatRoomPost**](DefaultApi.md#apigetchatroompostoperation) | **POST** /api/getChatRoom | Join the chat room |
| [**apiGetIdentifyStarsJobResultPost**](DefaultApi.md#apigetidentifystarsjobresultpostoperation) | **POST** /api/getIdentifyStarsJobResult | get identify stars job result. |
| [**apiGetLocationPost**](DefaultApi.md#apigetlocationpost) | **POST** /api/getLocation | Get current location |
| [**apiGetMessagePost**](DefaultApi.md#apigetmessagepostoperation) | **POST** /api/getMessage | Retrieve chat room messages |
| [**apiGetSavedBlogsPost**](DefaultApi.md#apigetsavedblogspostoperation) | **POST** /api/getSavedBlogs | List the blogs user saved |
| [**apiGetStarCatalogPost**](DefaultApi.md#apigetstarcatalogpost) | **POST** /api/getStarCatalog | Get star catalog |
| [**apiGetStarDetailsPost**](DefaultApi.md#apigetstardetailspostoperation) | **POST** /api/getStarDetails | calculate star details |
| [**apiLikeBlogPost**](DefaultApi.md#apilikeblogpost) | **POST** /api/likeBlog | Like a blog |
| [**apiListBlogsPost**](DefaultApi.md#apilistblogspostoperation) | **POST** /api/listBlogs | List all blogs under the certain star |
| [**apiListIdentifyStarsJobsPost**](DefaultApi.md#apilistidentifystarsjobspostoperation) | **POST** /api/listIdentifyStarsJobs | List identify stars jobs. |
| [**apiReportBlogPost**](DefaultApi.md#apireportblogpost) | **POST** /api/reportBlog | Report a blog |
| [**apiRequestAccuracyAdjustPost**](DefaultApi.md#apirequestaccuracyadjustpostoperation) | **POST** /api/requestAccuracyAdjust | Request accuracy adjustment |
| [**apiRequestSaveTypePost**](DefaultApi.md#apirequestsavetypepost) | **POST** /api/requestSaveType | Request save type options |
| [**apiRequestStargazingTimePost**](DefaultApi.md#apirequeststargazingtimepostoperation) | **POST** /api/requestStargazingTime | Request optimal stargazing time |
| [**apiSaveBlogPost**](DefaultApi.md#apisaveblogpost) | **POST** /api/saveBlog | Save a blog |
| [**apiSendMessagePost**](DefaultApi.md#apisendmessagepostoperation) | **POST** /api/sendMessage | Send message to chat room |
| [**apiSetUserPost**](DefaultApi.md#apisetuserpost) | **POST** /api/setUser | Set/modify username and password |
| [**apiTriggerStarfieldRenderPost**](DefaultApi.md#apitriggerstarfieldrenderpostoperation) | **POST** /api/triggerStarfieldRender | Trigger starfield rendering |
| [**apiUserLoginPost**](DefaultApi.md#apiuserloginpost) | **POST** /api/userLogin | User login |
| [**apiUserRegPost**](DefaultApi.md#apiuserregpostoperation) | **POST** /api/userReg | User register |
| [**apiUsernameVerifyPost**](DefaultApi.md#apiusernameverifypostoperation) | **POST** /api/usernameVerify | Verify the username |
| [**apiVerifyUserTokenPost**](DefaultApi.md#apiverifyusertokenpostoperation) | **POST** /api/verifyUserToken | Verify the user\&#39;s Token |
| [**apiViewBlogPost**](DefaultApi.md#apiviewblogpostoperation) | **POST** /api/viewBlog | Details of one blog |



## apiCalculateStarCoordinatesPost

> ApiCalculateStarCoordinatesPost200Response apiCalculateStarCoordinatesPost(apiCalculateStarCoordinatesPostRequest)

calculate star coordinates

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiCalculateStarCoordinatesPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiCalculateStarCoordinatesPostRequest (optional)
    apiCalculateStarCoordinatesPostRequest: ...,
  } satisfies ApiCalculateStarCoordinatesPostOperationRequest;

  try {
    const data = await api.apiCalculateStarCoordinatesPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiCalculateStarCoordinatesPostRequest** | [ApiCalculateStarCoordinatesPostRequest](ApiCalculateStarCoordinatesPostRequest.md) |  | [Optional] |

### Return type

[**ApiCalculateStarCoordinatesPost200Response**](ApiCalculateStarCoordinatesPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiChangePasswordPost

> ApiChangePasswordPost200Response apiChangePasswordPost(changePasswordRequest)



### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiChangePasswordPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ChangePasswordRequest
    changePasswordRequest: ...,
  } satisfies ApiChangePasswordPostRequest;

  try {
    const data = await api.apiChangePasswordPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **changePasswordRequest** | [ChangePasswordRequest](ChangePasswordRequest.md) |  | |

### Return type

[**ApiChangePasswordPost200Response**](ApiChangePasswordPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Password updated successfully |  -  |
| **401** | Old password incorrect |  -  |
| **404** | User not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiCheckRoomStatusPost

> ApiCheckRoomStatusPost200Response apiCheckRoomStatusPost(apiCheckRoomStatusPostRequest)

Check chat room status

Determines if a user can join the specified chat room

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiCheckRoomStatusPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiCheckRoomStatusPostRequest (optional)
    apiCheckRoomStatusPostRequest: ...,
  } satisfies ApiCheckRoomStatusPostOperationRequest;

  try {
    const data = await api.apiCheckRoomStatusPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiCheckRoomStatusPostRequest** | [ApiCheckRoomStatusPostRequest](ApiCheckRoomStatusPostRequest.md) |  | [Optional] |

### Return type

[**ApiCheckRoomStatusPost200Response**](ApiCheckRoomStatusPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Room status retrieved successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiCommentBlogPost

> ApiCommentBlogPost200Response apiCommentBlogPost(apiCommentBlogPostRequest)

Comment a blog

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiCommentBlogPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiCommentBlogPostRequest (optional)
    apiCommentBlogPostRequest: ...,
  } satisfies ApiCommentBlogPostOperationRequest;

  try {
    const data = await api.apiCommentBlogPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiCommentBlogPostRequest** | [ApiCommentBlogPostRequest](ApiCommentBlogPostRequest.md) |  | [Optional] |

### Return type

[**ApiCommentBlogPost200Response**](ApiCommentBlogPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiCreateBlogPost

> ApiCreateBlogPost200Response apiCreateBlogPost(apiCreateBlogPostRequest)

Create a new blog

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiCreateBlogPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiCreateBlogPostRequest (optional)
    apiCreateBlogPostRequest: ...,
  } satisfies ApiCreateBlogPostOperationRequest;

  try {
    const data = await api.apiCreateBlogPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiCreateBlogPostRequest** | [ApiCreateBlogPostRequest](ApiCreateBlogPostRequest.md) |  | [Optional] |

### Return type

[**ApiCreateBlogPost200Response**](ApiCreateBlogPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiCreateIdentifyStarsJobPost

> ApiCreateIdentifyStarsJobPost200Response apiCreateIdentifyStarsJobPost(image, userCredentials)

Create a job to identify the stars in the image.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiCreateIdentifyStarsJobPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // Blob | Image file to identify stars (JPEG, PNG, etc.)
    image: BINARY_DATA_HERE,
    // UserCredentials (optional)
    userCredentials: ...,
  } satisfies ApiCreateIdentifyStarsJobPostRequest;

  try {
    const data = await api.apiCreateIdentifyStarsJobPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **image** | `Blob` | Image file to identify stars (JPEG, PNG, etc.) | [Defaults to `undefined`] |
| **userCredentials** | [UserCredentials](UserCredentials.md) |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ApiCreateIdentifyStarsJobPost200Response**](ApiCreateIdentifyStarsJobPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `multipart/form-data`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiDeleteBlogPost

> ApiDeleteBlogPost200Response apiDeleteBlogPost(apiGetSavedBlogsPostRequest)

Delete a blog

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiDeleteBlogPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiGetSavedBlogsPostRequest (optional)
    apiGetSavedBlogsPostRequest: ...,
  } satisfies ApiDeleteBlogPostRequest;

  try {
    const data = await api.apiDeleteBlogPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiGetSavedBlogsPostRequest** | [ApiGetSavedBlogsPostRequest](ApiGetSavedBlogsPostRequest.md) |  | [Optional] |

### Return type

[**ApiDeleteBlogPost200Response**](ApiDeleteBlogPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiDeleteCommentPost

> ApiCommentBlogPost200Response apiDeleteCommentPost(apiDeleteCommentPostRequest)

Delete a comment

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiDeleteCommentPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiDeleteCommentPostRequest (optional)
    apiDeleteCommentPostRequest: ...,
  } satisfies ApiDeleteCommentPostOperationRequest;

  try {
    const data = await api.apiDeleteCommentPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiDeleteCommentPostRequest** | [ApiDeleteCommentPostRequest](ApiDeleteCommentPostRequest.md) |  | [Optional] |

### Return type

[**ApiCommentBlogPost200Response**](ApiCommentBlogPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiDeleteUserPost

> ApiChangePasswordPost200Response apiDeleteUserPost(userAuth)

注销账号

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiDeleteUserPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // UserAuth
    userAuth: ...,
  } satisfies ApiDeleteUserPostRequest;

  try {
    const data = await api.apiDeleteUserPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **userAuth** | [UserAuth](UserAuth.md) |  | |

### Return type

[**ApiChangePasswordPost200Response**](ApiChangePasswordPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Deletion successful |  -  |
| **401** | Password incorrect |  -  |
| **404** | User not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiDisplayChatRoomGet

> ApiDisplayChatRoomGet200Response apiDisplayChatRoomGet()

Display chat room entry button in GUI

Returns data to render chat room entry button in the graphical interface

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiDisplayChatRoomGetRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  try {
    const data = await api.apiDisplayChatRoomGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**ApiDisplayChatRoomGet200Response**](ApiDisplayChatRoomGet200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Button configuration retrieved successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiDisplaySaveSuccessPost

> ApiDisplaySaveSuccessPost200Response apiDisplaySaveSuccessPost(apiDisplaySaveSuccessPostRequest)

Display save success confirmation

Return save result and metadata after starfield is saved

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiDisplaySaveSuccessPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiDisplaySaveSuccessPostRequest (optional)
    apiDisplaySaveSuccessPostRequest: ...,
  } satisfies ApiDisplaySaveSuccessPostOperationRequest;

  try {
    const data = await api.apiDisplaySaveSuccessPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiDisplaySaveSuccessPostRequest** | [ApiDisplaySaveSuccessPostRequest](ApiDisplaySaveSuccessPostRequest.md) |  | [Optional] |

### Return type

[**ApiDisplaySaveSuccessPost200Response**](ApiDisplaySaveSuccessPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiDisplayStarDetailsPost

> StarDetails apiDisplayStarDetailsPost(apiDisplayStarDetailsPostRequest)

Display star details

Retrieve detailed astronomical information of a specific star

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiDisplayStarDetailsPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiDisplayStarDetailsPostRequest (optional)
    apiDisplayStarDetailsPostRequest: ...,
  } satisfies ApiDisplayStarDetailsPostOperationRequest;

  try {
    const data = await api.apiDisplayStarDetailsPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiDisplayStarDetailsPostRequest** | [ApiDisplayStarDetailsPostRequest](ApiDisplayStarDetailsPostRequest.md) |  | [Optional] |

### Return type

[**StarDetails**](StarDetails.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiDisplayStarfieldPost

> ApiDisplayStarfieldPost200Response apiDisplayStarfieldPost(apiDisplayStarfieldPostRequest)

Display starfield

Retrieve rendered starfield data for GUI display

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiDisplayStarfieldPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiDisplayStarfieldPostRequest (optional)
    apiDisplayStarfieldPostRequest: ...,
  } satisfies ApiDisplayStarfieldPostOperationRequest;

  try {
    const data = await api.apiDisplayStarfieldPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiDisplayStarfieldPostRequest** | [ApiDisplayStarfieldPostRequest](ApiDisplayStarfieldPostRequest.md) |  | [Optional] |

### Return type

[**ApiDisplayStarfieldPost200Response**](ApiDisplayStarfieldPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiElimilateErrorsPost

> ApiElimilateErrorsPost200Response apiElimilateErrorsPost(apiElimilateErrorsPostRequest)

Eliminating the errors between the stars\&#39; positions that we calculated and the stars\&#39; positions captured by the camera. These errors are generally caused by the limited accuracy of the sensor.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiElimilateErrorsPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiElimilateErrorsPostRequest (optional)
    apiElimilateErrorsPostRequest: ...,
  } satisfies ApiElimilateErrorsPostOperationRequest;

  try {
    const data = await api.apiElimilateErrorsPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiElimilateErrorsPostRequest** | [ApiElimilateErrorsPostRequest](ApiElimilateErrorsPostRequest.md) |  | [Optional] |

### Return type

[**ApiElimilateErrorsPost200Response**](ApiElimilateErrorsPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiExitChatRoomPost

> ApiExitChatRoomPost200Response apiExitChatRoomPost(apiExitChatRoomPostRequest)

Exit chat room

Updates user\&#39;s participation status and triggers related notifications

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiExitChatRoomPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiExitChatRoomPostRequest
    apiExitChatRoomPostRequest: ...,
  } satisfies ApiExitChatRoomPostOperationRequest;

  try {
    const data = await api.apiExitChatRoomPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiExitChatRoomPostRequest** | [ApiExitChatRoomPostRequest](ApiExitChatRoomPostRequest.md) |  | |

### Return type

[**ApiExitChatRoomPost200Response**](ApiExitChatRoomPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successfully exited chat room |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiGetAttitudePost

> Attitude apiGetAttitudePost()

Get attitude of the mobile device

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiGetAttitudePostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  try {
    const data = await api.apiGetAttitudePost();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Attitude**](Attitude.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiGetCameraDataPost

> ApiGetCameraDataPost200Response apiGetCameraDataPost()

Get camera data

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiGetCameraDataPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  try {
    const data = await api.apiGetCameraDataPost();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**ApiGetCameraDataPost200Response**](ApiGetCameraDataPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiGetChatRoomInfoPost

> ApiGetChatRoomInfoPost200Response apiGetChatRoomInfoPost(apiGetChatRoomInfoPostRequest)

Retrieve chat room from social system

Gets specified chat room information from the social system

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiGetChatRoomInfoPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiGetChatRoomInfoPostRequest (optional)
    apiGetChatRoomInfoPostRequest: ...,
  } satisfies ApiGetChatRoomInfoPostOperationRequest;

  try {
    const data = await api.apiGetChatRoomInfoPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiGetChatRoomInfoPostRequest** | [ApiGetChatRoomInfoPostRequest](ApiGetChatRoomInfoPostRequest.md) |  | [Optional] |

### Return type

[**ApiGetChatRoomInfoPost200Response**](ApiGetChatRoomInfoPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Chat room information retrieved successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiGetChatRoomPost

> ApiGetChatRoomPost200Response apiGetChatRoomPost(apiGetChatRoomPostRequest)

Join the chat room

Join the chat room

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiGetChatRoomPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiGetChatRoomPostRequest
    apiGetChatRoomPostRequest: ...,
  } satisfies ApiGetChatRoomPostOperationRequest;

  try {
    const data = await api.apiGetChatRoomPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiGetChatRoomPostRequest** | [ApiGetChatRoomPostRequest](ApiGetChatRoomPostRequest.md) |  | |

### Return type

[**ApiGetChatRoomPost200Response**](ApiGetChatRoomPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successfully entered the chat room |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiGetIdentifyStarsJobResultPost

> ApiGetIdentifyStarsJobResultPost200Response apiGetIdentifyStarsJobResultPost(apiGetIdentifyStarsJobResultPostRequest)

get identify stars job result.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiGetIdentifyStarsJobResultPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiGetIdentifyStarsJobResultPostRequest
    apiGetIdentifyStarsJobResultPostRequest: ...,
  } satisfies ApiGetIdentifyStarsJobResultPostOperationRequest;

  try {
    const data = await api.apiGetIdentifyStarsJobResultPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiGetIdentifyStarsJobResultPostRequest** | [ApiGetIdentifyStarsJobResultPostRequest](ApiGetIdentifyStarsJobResultPostRequest.md) |  | |

### Return type

[**ApiGetIdentifyStarsJobResultPost200Response**](ApiGetIdentifyStarsJobResultPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiGetLocationPost

> GPS apiGetLocationPost()

Get current location

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiGetLocationPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  try {
    const data = await api.apiGetLocationPost();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**GPS**](GPS.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiGetMessagePost

> ApiGetMessagePost200Response apiGetMessagePost(apiGetMessagePostRequest)

Retrieve chat room messages

Gets historical and real-time messages from the chat room

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiGetMessagePostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiGetMessagePostRequest
    apiGetMessagePostRequest: ...,
  } satisfies ApiGetMessagePostOperationRequest;

  try {
    const data = await api.apiGetMessagePost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiGetMessagePostRequest** | [ApiGetMessagePostRequest](ApiGetMessagePostRequest.md) |  | |

### Return type

[**ApiGetMessagePost200Response**](ApiGetMessagePost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Messages retrieved successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiGetSavedBlogsPost

> ApiGetSavedBlogsPost200Response apiGetSavedBlogsPost(apiGetSavedBlogsPostRequest)

List the blogs user saved

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiGetSavedBlogsPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiGetSavedBlogsPostRequest (optional)
    apiGetSavedBlogsPostRequest: ...,
  } satisfies ApiGetSavedBlogsPostOperationRequest;

  try {
    const data = await api.apiGetSavedBlogsPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiGetSavedBlogsPostRequest** | [ApiGetSavedBlogsPostRequest](ApiGetSavedBlogsPostRequest.md) |  | [Optional] |

### Return type

[**ApiGetSavedBlogsPost200Response**](ApiGetSavedBlogsPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiGetStarCatalogPost

> ApiGetStarCatalogPost200Response apiGetStarCatalogPost()

Get star catalog

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiGetStarCatalogPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  try {
    const data = await api.apiGetStarCatalogPost();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**ApiGetStarCatalogPost200Response**](ApiGetStarCatalogPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiGetStarDetailsPost

> StarDetails apiGetStarDetailsPost(apiGetStarDetailsPostRequest)

calculate star details

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiGetStarDetailsPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiGetStarDetailsPostRequest (optional)
    apiGetStarDetailsPostRequest: ...,
  } satisfies ApiGetStarDetailsPostOperationRequest;

  try {
    const data = await api.apiGetStarDetailsPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiGetStarDetailsPostRequest** | [ApiGetStarDetailsPostRequest](ApiGetStarDetailsPostRequest.md) |  | [Optional] |

### Return type

[**StarDetails**](StarDetails.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiLikeBlogPost

> ApiLikeBlogPost200Response apiLikeBlogPost(apiGetSavedBlogsPostRequest)

Like a blog

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiLikeBlogPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiGetSavedBlogsPostRequest (optional)
    apiGetSavedBlogsPostRequest: ...,
  } satisfies ApiLikeBlogPostRequest;

  try {
    const data = await api.apiLikeBlogPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiGetSavedBlogsPostRequest** | [ApiGetSavedBlogsPostRequest](ApiGetSavedBlogsPostRequest.md) |  | [Optional] |

### Return type

[**ApiLikeBlogPost200Response**](ApiLikeBlogPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiListBlogsPost

> ApiListBlogsPost200Response apiListBlogsPost(apiListBlogsPostRequest)

List all blogs under the certain star

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiListBlogsPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiListBlogsPostRequest (optional)
    apiListBlogsPostRequest: ...,
  } satisfies ApiListBlogsPostOperationRequest;

  try {
    const data = await api.apiListBlogsPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiListBlogsPostRequest** | [ApiListBlogsPostRequest](ApiListBlogsPostRequest.md) |  | [Optional] |

### Return type

[**ApiListBlogsPost200Response**](ApiListBlogsPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiListIdentifyStarsJobsPost

> ApiListIdentifyStarsJobsPost200Response apiListIdentifyStarsJobsPost(apiListIdentifyStarsJobsPostRequest)

List identify stars jobs.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiListIdentifyStarsJobsPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiListIdentifyStarsJobsPostRequest (optional)
    apiListIdentifyStarsJobsPostRequest: ...,
  } satisfies ApiListIdentifyStarsJobsPostOperationRequest;

  try {
    const data = await api.apiListIdentifyStarsJobsPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiListIdentifyStarsJobsPostRequest** | [ApiListIdentifyStarsJobsPostRequest](ApiListIdentifyStarsJobsPostRequest.md) |  | [Optional] |

### Return type

[**ApiListIdentifyStarsJobsPost200Response**](ApiListIdentifyStarsJobsPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiReportBlogPost

> ApiDeleteBlogPost200Response apiReportBlogPost(apiGetSavedBlogsPostRequest)

Report a blog

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiReportBlogPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiGetSavedBlogsPostRequest (optional)
    apiGetSavedBlogsPostRequest: ...,
  } satisfies ApiReportBlogPostRequest;

  try {
    const data = await api.apiReportBlogPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiGetSavedBlogsPostRequest** | [ApiGetSavedBlogsPostRequest](ApiGetSavedBlogsPostRequest.md) |  | [Optional] |

### Return type

[**ApiDeleteBlogPost200Response**](ApiDeleteBlogPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiRequestAccuracyAdjustPost

> ApiRequestAccuracyAdjustPost200Response apiRequestAccuracyAdjustPost(apiRequestAccuracyAdjustPostRequest)

Request accuracy adjustment

Adjust calculation accuracy for star coordinates based on sensor precision

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiRequestAccuracyAdjustPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiRequestAccuracyAdjustPostRequest (optional)
    apiRequestAccuracyAdjustPostRequest: ...,
  } satisfies ApiRequestAccuracyAdjustPostOperationRequest;

  try {
    const data = await api.apiRequestAccuracyAdjustPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiRequestAccuracyAdjustPostRequest** | [ApiRequestAccuracyAdjustPostRequest](ApiRequestAccuracyAdjustPostRequest.md) |  | [Optional] |

### Return type

[**ApiRequestAccuracyAdjustPost200Response**](ApiRequestAccuracyAdjustPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiRequestSaveTypePost

> ApiRequestSaveTypePost200Response apiRequestSaveTypePost()

Request save type options

Get available save types for rendered starfield

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiRequestSaveTypePostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  try {
    const data = await api.apiRequestSaveTypePost();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**ApiRequestSaveTypePost200Response**](ApiRequestSaveTypePost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiRequestStargazingTimePost

> ApiRequestStargazingTimePost200Response apiRequestStargazingTimePost(apiRequestStargazingTimePostRequest)

Request optimal stargazing time

Get recommended stargazing time range based on GPS location

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiRequestStargazingTimePostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiRequestStargazingTimePostRequest (optional)
    apiRequestStargazingTimePostRequest: ...,
  } satisfies ApiRequestStargazingTimePostOperationRequest;

  try {
    const data = await api.apiRequestStargazingTimePost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiRequestStargazingTimePostRequest** | [ApiRequestStargazingTimePostRequest](ApiRequestStargazingTimePostRequest.md) |  | [Optional] |

### Return type

[**ApiRequestStargazingTimePost200Response**](ApiRequestStargazingTimePost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiSaveBlogPost

> ApiDeleteBlogPost200Response apiSaveBlogPost(apiGetSavedBlogsPostRequest)

Save a blog

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiSaveBlogPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiGetSavedBlogsPostRequest (optional)
    apiGetSavedBlogsPostRequest: ...,
  } satisfies ApiSaveBlogPostRequest;

  try {
    const data = await api.apiSaveBlogPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiGetSavedBlogsPostRequest** | [ApiGetSavedBlogsPostRequest](ApiGetSavedBlogsPostRequest.md) |  | [Optional] |

### Return type

[**ApiDeleteBlogPost200Response**](ApiDeleteBlogPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiSendMessagePost

> ApiSendMessagePost200Response apiSendMessagePost(apiSendMessagePostRequest)

Send message to chat room

Sends a message to the specified chat room for real-time communication

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiSendMessagePostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiSendMessagePostRequest
    apiSendMessagePostRequest: ...,
  } satisfies ApiSendMessagePostOperationRequest;

  try {
    const data = await api.apiSendMessagePost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiSendMessagePostRequest** | [ApiSendMessagePostRequest](ApiSendMessagePostRequest.md) |  | |

### Return type

[**ApiSendMessagePost200Response**](ApiSendMessagePost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Message sent successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiSetUserPost

> ApiSetUserPost200Response apiSetUserPost(changePasswordRequest)

Set/modify username and password

Modify the username and password by the username, current password(password0)and new password(password1) user provided.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiSetUserPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ChangePasswordRequest
    changePasswordRequest: ...,
  } satisfies ApiSetUserPostRequest;

  try {
    const data = await api.apiSetUserPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **changePasswordRequest** | [ChangePasswordRequest](ChangePasswordRequest.md) |  | |

### Return type

[**ApiSetUserPost200Response**](ApiSetUserPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Modify password successful. |  -  |
| **400** | Invalid request: For example, the new password does not meet the security requirements, or the new and old passwords are the same. |  -  |
| **401** | Unauthorized: Current password (password0) is incorrect |  -  |
| **404** | Not Found: The username does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiTriggerStarfieldRenderPost

> ApiTriggerStarfieldRenderPost200Response apiTriggerStarfieldRenderPost(apiTriggerStarfieldRenderPostRequest)

Trigger starfield rendering

Initiate starfield rendering process using corrected star coordinates and camera parameters

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiTriggerStarfieldRenderPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiTriggerStarfieldRenderPostRequest (optional)
    apiTriggerStarfieldRenderPostRequest: ...,
  } satisfies ApiTriggerStarfieldRenderPostOperationRequest;

  try {
    const data = await api.apiTriggerStarfieldRenderPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiTriggerStarfieldRenderPostRequest** | [ApiTriggerStarfieldRenderPostRequest](ApiTriggerStarfieldRenderPostRequest.md) |  | [Optional] |

### Return type

[**ApiTriggerStarfieldRenderPost200Response**](ApiTriggerStarfieldRenderPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiUserLoginPost

> TokenResponse apiUserLoginPost(userAuth)

User login

Use username and password to authentication, return a token if success.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiUserLoginPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // UserAuth
    userAuth: ...,
  } satisfies ApiUserLoginPostRequest;

  try {
    const data = await api.apiUserLoginPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **userAuth** | [UserAuth](UserAuth.md) |  | |

### Return type

[**TokenResponse**](TokenResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Login successful. |  -  |
| **401** | Unauthorized: Incorrect username or password. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiUserRegPost

> UserResponse apiUserRegPost(apiUserRegPostRequest)

User register

Create an account with a new username and password.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiUserRegPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiUserRegPostRequest
    apiUserRegPostRequest: ...,
  } satisfies ApiUserRegPostOperationRequest;

  try {
    const data = await api.apiUserRegPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiUserRegPostRequest** | [ApiUserRegPostRequest](ApiUserRegPostRequest.md) |  | |

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Create user successful. |  -  |
| **400** | Invalid request: For example, the password does not meet the requirements. |  -  |
| **409** | Conflict: The username is already in use. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiUsernameVerifyPost

> ApiUsernameVerifyPost200Response apiUsernameVerifyPost(apiUsernameVerifyPostRequest)

Verify the username

Check whether the username is available.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiUsernameVerifyPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiUsernameVerifyPostRequest
    apiUsernameVerifyPostRequest: ...,
  } satisfies ApiUsernameVerifyPostOperationRequest;

  try {
    const data = await api.apiUsernameVerifyPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiUsernameVerifyPostRequest** | [ApiUsernameVerifyPostRequest](ApiUsernameVerifyPostRequest.md) |  | |

### Return type

[**ApiUsernameVerifyPost200Response**](ApiUsernameVerifyPost200Response.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Username available |  -  |
| **409** | The username is already in use. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiVerifyUserTokenPost

> UserResponse apiVerifyUserTokenPost(apiVerifyUserTokenPostRequest)

Verify the user\&#39;s Token

Check whether the provided Token is valid. If it is valid, return the corresponding user information.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiVerifyUserTokenPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiVerifyUserTokenPostRequest
    apiVerifyUserTokenPostRequest: ...,
  } satisfies ApiVerifyUserTokenPostOperationRequest;

  try {
    const data = await api.apiVerifyUserTokenPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiVerifyUserTokenPostRequest** | [ApiVerifyUserTokenPostRequest](ApiVerifyUserTokenPostRequest.md) |  | |

### Return type

[**UserResponse**](UserResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Token is valid. |  -  |
| **401** | Invalid or expired Token. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiViewBlogPost

> Blog apiViewBlogPost(apiViewBlogPostRequest)

Details of one blog

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiViewBlogPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiViewBlogPostRequest (optional)
    apiViewBlogPostRequest: ...,
  } satisfies ApiViewBlogPostOperationRequest;

  try {
    const data = await api.apiViewBlogPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **apiViewBlogPostRequest** | [ApiViewBlogPostRequest](ApiViewBlogPostRequest.md) |  | [Optional] |

### Return type

[**Blog**](Blog.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

