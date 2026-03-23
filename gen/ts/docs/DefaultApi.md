# DefaultApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**apiCalculateStarCoordinatesPost**](DefaultApi.md#apicalculatestarcoordinatespostoperation) | **POST** /api/calculateStarCoordinates | calculate star coordinates |
| [**apiChangePasswordPost**](DefaultApi.md#apichangepasswordpost) | **POST** /api/changePassword |  |
| [**apiCheckRoomStatusPost**](DefaultApi.md#apicheckroomstatuspostoperation) | **POST** /api/checkRoomStatus | Check chat room status |
| [**apiCommentBlogPost**](DefaultApi.md#apicommentblogpostoperation) | **POST** /api/commentBlog | Comment a blog |
| [**apiCreateBlogPost**](DefaultApi.md#apicreateblogpostoperation) | **POST** /api/createBlog | Create a new blog |
| [**apiCreateIdentifyStarsJobPost**](DefaultApi.md#apicreateidentifystarsjobpostoperation) | **POST** /api/createIdentifyStarsJob | Create a job to identify the stars in the image. |
| [**apiDeleteBlogPost**](DefaultApi.md#apideleteblogpost) | **POST** /api/deleteBlog | Delete a blog |
| [**apiDeleteCommentPost**](DefaultApi.md#apideletecommentpostoperation) | **POST** /api/deleteComment | Delete a comment |
| [**apiDeleteUserPost**](DefaultApi.md#apideleteuserpost) | **POST** /api/deleteUser | 注销账号 |
| [**apiDisplayChatRoomGet**](DefaultApi.md#apidisplaychatroomget) | **GET** /api/displayChatRoom | Display chat room entry button in GUI |
| [**apiDisplaySaveSuccessPost**](DefaultApi.md#apidisplaysavesuccesspostoperation) | **POST** /api/displaySaveSuccess | Display save success confirmation |
| [**apiDisplayStarDetailsPost**](DefaultApi.md#apidisplaystardetailspostoperation) | **POST** /api/displayStarDetails | Display star details |
| [**apiDisplayStarfieldPost**](DefaultApi.md#apidisplaystarfieldpostoperation) | **POST** /api/displayStarfield | Display starfield |
| [**apiEditProfilePost**](DefaultApi.md#apieditprofilepost) | **POST** /api/editProfile |  update user profile |
| [**apiElimilateErrorsPost**](DefaultApi.md#apielimilateerrorspostoperation) | **POST** /api/elimilateErrors | Eliminating the errors between the stars\&#39; positions that we calculated and the stars\&#39; positions captured by the camera. These errors are generally caused by the limited accuracy of the sensor. |
| [**apiExitChatRoomPost**](DefaultApi.md#apiexitchatroompostoperation) | **POST** /api/exitChatRoom | Exit chat room |
| [**apiGetAttitudePost**](DefaultApi.md#apigetattitudepost) | **POST** /api/getAttitude | Get attitude of the mobile device |
| [**apiGetCameraDataPost**](DefaultApi.md#apigetcameradatapost) | **POST** /api/getCameraData | Get camera data |
| [**apiGetChatRoomInfoPost**](DefaultApi.md#apigetchatroominfopostoperation) | **POST** /api/getChatRoomInfo | Retrieve chat room from social system |
| [**apiGetChatRoomPost**](DefaultApi.md#apigetchatroompostoperation) | **POST** /api/getChatRoom | Join the chat room |
| [**apiGetIdentifyStarsJobResultPost**](DefaultApi.md#apigetidentifystarsjobresultpostoperation) | **POST** /api/getIdentifyStarsJobResult | get identify stars job result. |
| [**apiGetLocationPost**](DefaultApi.md#apigetlocationpost) | **POST** /api/getLocation | Get current location |
| [**apiGetMessagePost**](DefaultApi.md#apigetmessagepostoperation) | **POST** /api/getMessage | Retrieve chat room messages |
| [**apiGetProfileStatsPost**](DefaultApi.md#apigetprofilestatspost) | **POST** /api/getProfileStats | Get user profile stats |
| [**apiGetStarCatalogPost**](DefaultApi.md#apigetstarcatalogpost) | **POST** /api/getStarCatalog | Get star catalog |
| [**apiGetStarDetailsPost**](DefaultApi.md#apigetstardetailspostoperation) | **POST** /api/getStarDetails | calculate star details |
| [**apiHealthGet**](DefaultApi.md#apihealthget) | **GET** /api/health | health check |
| [**apiLikeBlogPost**](DefaultApi.md#apilikeblogpost) | **POST** /api/likeBlog | Like a blog |
| [**apiListIdentifyStarsJobsPost**](DefaultApi.md#apilistidentifystarsjobspost) | **POST** /api/listIdentifyStarsJobs | List identify stars jobs. |
| [**apiListSavedBlogsPost**](DefaultApi.md#apilistsavedblogspost) | **POST** /api/listSavedBlogs | List all blogs saved by the user |
| [**apiListStarBlogsPost**](DefaultApi.md#apiliststarblogspostoperation) | **POST** /api/listStarBlogs | List all blogs under the certain star |
| [**apiListUserBlogsPost**](DefaultApi.md#apilistuserblogspost) | **POST** /api/listUserBlogs | List all blogs posted by a specific user |
| [**apiReportBlogPost**](DefaultApi.md#apireportblogpostoperation) | **POST** /api/reportBlog | Report a blog |
| [**apiRequestAccuracyAdjustPost**](DefaultApi.md#apirequestaccuracyadjustpostoperation) | **POST** /api/requestAccuracyAdjust | Request accuracy adjustment |
| [**apiRequestSaveTypePost**](DefaultApi.md#apirequestsavetypepost) | **POST** /api/requestSaveType | Request save type options |
| [**apiRequestStargazingTimePost**](DefaultApi.md#apirequeststargazingtimepostoperation) | **POST** /api/requestStargazingTime | Request optimal stargazing time |
| [**apiResetPasswordPost**](DefaultApi.md#apiresetpasswordpost) | **POST** /api/resetPassword | Use code to reset password |
| [**apiResetPasswordSendCodePost**](DefaultApi.md#apiresetpasswordsendcodepost) | **POST** /api/resetPasswordSendCode | send code to email |
| [**apiSaveBlogPost**](DefaultApi.md#apisaveblogpost) | **POST** /api/saveBlog | Save a blog |
| [**apiSendMessagePost**](DefaultApi.md#apisendmessagepostoperation) | **POST** /api/sendMessage | Send message to chat room |
| [**apiSetUserPost**](DefaultApi.md#apisetuserpost) | **POST** /api/setUser | Set/modify username and password |
| [**apiTriggerStarfieldRenderPost**](DefaultApi.md#apitriggerstarfieldrenderpostoperation) | **POST** /api/triggerStarfieldRender | Trigger starfield rendering |
| [**apiUpdateLastGpsPost**](DefaultApi.md#apiupdatelastgpspost) | **POST** /api/updateLastGps | update user last gps |
| [**apiUploadBlogImagePost**](DefaultApi.md#apiuploadblogimagepostoperation) | **POST** /api/uploadBlogImage | Upload a blog image and get back a URL |
| [**apiUserLoginPost**](DefaultApi.md#apiuserloginpost) | **POST** /api/userLogin | User login |
| [**apiUserRegPost**](DefaultApi.md#apiuserregpostoperation) | **POST** /api/userReg | User register |
| [**apiUsernameVerifyPost**](DefaultApi.md#apiusernameverifypostoperation) | **POST** /api/usernameVerify | Verify the username |
| [**apiVerifyUserTokenPost**](DefaultApi.md#apiverifyusertokenpostoperation) | **POST** /api/verifyUserToken | Verify the user\&#39;s Token |
| [**apiViewBlogPost**](DefaultApi.md#apiviewblogpost) | **POST** /api/viewBlog | Details of one blog |



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
    // ApiCalculateStarCoordinatesPostRequest
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
| **apiCalculateStarCoordinatesPostRequest** | [ApiCalculateStarCoordinatesPostRequest](ApiCalculateStarCoordinatesPostRequest.md) |  | |

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

> CommonMessage apiChangePasswordPost(changePasswordRequest)



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

[**CommonMessage**](CommonMessage.md)

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
    // ApiCheckRoomStatusPostRequest
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
| **apiCheckRoomStatusPostRequest** | [ApiCheckRoomStatusPostRequest](ApiCheckRoomStatusPostRequest.md) |  | |

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
    // ApiCommentBlogPostRequest
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
| **apiCommentBlogPostRequest** | [ApiCommentBlogPostRequest](ApiCommentBlogPostRequest.md) |  | |

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
    // ApiCreateBlogPostRequest
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
| **apiCreateBlogPostRequest** | [ApiCreateBlogPostRequest](ApiCreateBlogPostRequest.md) |  | |

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

> ApiCreateIdentifyStarsJobPost200Response apiCreateIdentifyStarsJobPost(apiCreateIdentifyStarsJobPostRequest)

Create a job to identify the stars in the image.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiCreateIdentifyStarsJobPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiCreateIdentifyStarsJobPostRequest
    apiCreateIdentifyStarsJobPostRequest: ...,
  } satisfies ApiCreateIdentifyStarsJobPostOperationRequest;

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
| **apiCreateIdentifyStarsJobPostRequest** | [ApiCreateIdentifyStarsJobPostRequest](ApiCreateIdentifyStarsJobPostRequest.md) |  | |

### Return type

[**ApiCreateIdentifyStarsJobPost200Response**](ApiCreateIdentifyStarsJobPost200Response.md)

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


## apiDeleteBlogPost

> BlogID apiDeleteBlogPost(blogID)

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
    // BlogID
    blogID: ...,
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
| **blogID** | [BlogID](BlogID.md) |  | |

### Return type

[**BlogID**](BlogID.md)

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
    // ApiDeleteCommentPostRequest
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
| **apiDeleteCommentPostRequest** | [ApiDeleteCommentPostRequest](ApiDeleteCommentPostRequest.md) |  | |

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

> CommonMessage apiDeleteUserPost(userAuth)

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

[**CommonMessage**](CommonMessage.md)

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
    // ApiDisplaySaveSuccessPostRequest
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
| **apiDisplaySaveSuccessPostRequest** | [ApiDisplaySaveSuccessPostRequest](ApiDisplaySaveSuccessPostRequest.md) |  | |

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
    // ApiDisplayStarDetailsPostRequest
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
| **apiDisplayStarDetailsPostRequest** | [ApiDisplayStarDetailsPostRequest](ApiDisplayStarDetailsPostRequest.md) |  | |

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
    // ApiDisplayStarfieldPostRequest
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
| **apiDisplayStarfieldPostRequest** | [ApiDisplayStarfieldPostRequest](ApiDisplayStarfieldPostRequest.md) |  | |

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


## apiEditProfilePost

> UserResponse apiEditProfilePost(profileAndToken)

 update user profile

update the user\&#39;s profile information stored as JSON.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiEditProfilePostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ProfileAndToken
    profileAndToken: ...,
  } satisfies ApiEditProfilePostRequest;

  try {
    const data = await api.apiEditProfilePost(body);
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
| **profileAndToken** | [ProfileAndToken](ProfileAndToken.md) |  | |

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
| **200** | Profile updated successfully. |  -  |
| **400** | Invalid request: For example, invalid JSON format. |  -  |
| **401** | Unauthorized: Authentication required. |  -  |
| **404** | User not found. |  -  |

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
    // ApiElimilateErrorsPostRequest
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
| **apiElimilateErrorsPostRequest** | [ApiElimilateErrorsPostRequest](ApiElimilateErrorsPostRequest.md) |  | |

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
    // ApiGetChatRoomInfoPostRequest
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
| **apiGetChatRoomInfoPostRequest** | [ApiGetChatRoomInfoPostRequest](ApiGetChatRoomInfoPostRequest.md) |  | |

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


## apiGetProfileStatsPost

> ProfileStatsResponse apiGetProfileStatsPost(body)

Get user profile stats

Retrieve the user\&#39;s scanning statistics, rank, and join date for the profile view.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiGetProfileStatsPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // object
    body: Object,
  } satisfies ApiGetProfileStatsPostRequest;

  try {
    const data = await api.apiGetProfileStatsPost(body);
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
| **body** | `object` |  | |

### Return type

[**ProfileStatsResponse**](ProfileStatsResponse.md)

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
    // ApiGetStarDetailsPostRequest
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
| **apiGetStarDetailsPostRequest** | [ApiGetStarDetailsPostRequest](ApiGetStarDetailsPostRequest.md) |  | |

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


## apiHealthGet

> apiHealthGet()

health check

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiHealthGetRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  try {
    const data = await api.apiHealthGet();
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

`void` (Empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiLikeBlogPost

> ApiLikeBlogPost200Response apiLikeBlogPost(blogID)

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
    // BlogID
    blogID: ...,
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
| **blogID** | [BlogID](BlogID.md) |  | |

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


## apiListIdentifyStarsJobsPost

> ApiListIdentifyStarsJobsPost200Response apiListIdentifyStarsJobsPost(paginationQuery)

List identify stars jobs.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiListIdentifyStarsJobsPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // PaginationQuery
    paginationQuery: ...,
  } satisfies ApiListIdentifyStarsJobsPostRequest;

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
| **paginationQuery** | [PaginationQuery](PaginationQuery.md) |  | |

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


## apiListSavedBlogsPost

> BlogsList apiListSavedBlogsPost(paginationQuery)

List all blogs saved by the user

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiListSavedBlogsPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // PaginationQuery
    paginationQuery: ...,
  } satisfies ApiListSavedBlogsPostRequest;

  try {
    const data = await api.apiListSavedBlogsPost(body);
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
| **paginationQuery** | [PaginationQuery](PaginationQuery.md) |  | |

### Return type

[**BlogsList**](BlogsList.md)

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


## apiListStarBlogsPost

> BlogsList apiListStarBlogsPost(apiListStarBlogsPostRequest)

List all blogs under the certain star

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiListStarBlogsPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiListStarBlogsPostRequest
    apiListStarBlogsPostRequest: ...,
  } satisfies ApiListStarBlogsPostOperationRequest;

  try {
    const data = await api.apiListStarBlogsPost(body);
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
| **apiListStarBlogsPostRequest** | [ApiListStarBlogsPostRequest](ApiListStarBlogsPostRequest.md) |  | |

### Return type

[**BlogsList**](BlogsList.md)

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


## apiListUserBlogsPost

> BlogsList apiListUserBlogsPost(paginationQuery)

List all blogs posted by a specific user

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiListUserBlogsPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // PaginationQuery
    paginationQuery: ...,
  } satisfies ApiListUserBlogsPostRequest;

  try {
    const data = await api.apiListUserBlogsPost(body);
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
| **paginationQuery** | [PaginationQuery](PaginationQuery.md) |  | |

### Return type

[**BlogsList**](BlogsList.md)

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

> BlogID apiReportBlogPost(apiReportBlogPostRequest)

Report a blog

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiReportBlogPostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiReportBlogPostRequest
    apiReportBlogPostRequest: ...,
  } satisfies ApiReportBlogPostOperationRequest;

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
| **apiReportBlogPostRequest** | [ApiReportBlogPostRequest](ApiReportBlogPostRequest.md) |  | |

### Return type

[**BlogID**](BlogID.md)

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
    // ApiRequestAccuracyAdjustPostRequest
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
| **apiRequestAccuracyAdjustPostRequest** | [ApiRequestAccuracyAdjustPostRequest](ApiRequestAccuracyAdjustPostRequest.md) |  | |

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
    // ApiRequestStargazingTimePostRequest
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
| **apiRequestStargazingTimePostRequest** | [ApiRequestStargazingTimePostRequest](ApiRequestStargazingTimePostRequest.md) |  | |

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


## apiResetPasswordPost

> CommonMessage apiResetPasswordPost(resetPasswordRequest)

Use code to reset password

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiResetPasswordPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ResetPasswordRequest
    resetPasswordRequest: ...,
  } satisfies ApiResetPasswordPostRequest;

  try {
    const data = await api.apiResetPasswordPost(body);
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
| **resetPasswordRequest** | [ResetPasswordRequest](ResetPasswordRequest.md) |  | |

### Return type

[**CommonMessage**](CommonMessage.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Password reset successfully |  -  |
| **400** | Invalid or expired verification code |  -  |
| **404** | Email not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiResetPasswordSendCodePost

> CommonMessage apiResetPasswordSendCodePost(resetPasswordSendCodeRequest)

send code to email

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiResetPasswordSendCodePostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ResetPasswordSendCodeRequest
    resetPasswordSendCodeRequest: ...,
  } satisfies ApiResetPasswordSendCodePostRequest;

  try {
    const data = await api.apiResetPasswordSendCodePost(body);
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
| **resetPasswordSendCodeRequest** | [ResetPasswordSendCodeRequest](ResetPasswordSendCodeRequest.md) |  | |

### Return type

[**CommonMessage**](CommonMessage.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Verification code sent successfully |  -  |
| **404** | Email not found |  -  |
| **500** | Failed to send email |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiSaveBlogPost

> BlogID apiSaveBlogPost(blogID)

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
    // BlogID
    blogID: ...,
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
| **blogID** | [BlogID](BlogID.md) |  | |

### Return type

[**BlogID**](BlogID.md)

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

> CommonMessage apiSetUserPost(changePasswordRequest)

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

[**CommonMessage**](CommonMessage.md)

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
    // ApiTriggerStarfieldRenderPostRequest
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
| **apiTriggerStarfieldRenderPostRequest** | [ApiTriggerStarfieldRenderPostRequest](ApiTriggerStarfieldRenderPostRequest.md) |  | |

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


## apiUpdateLastGpsPost

> CommonMessage apiUpdateLastGpsPost(updateLastGpsRequest)

update user last gps

update the user\&#39;s latest GPS location used by recommendation emails.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiUpdateLastGpsPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // UpdateLastGpsRequest
    updateLastGpsRequest: ...,
  } satisfies ApiUpdateLastGpsPostRequest;

  try {
    const data = await api.apiUpdateLastGpsPost(body);
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
| **updateLastGpsRequest** | [UpdateLastGpsRequest](UpdateLastGpsRequest.md) |  | |

### Return type

[**CommonMessage**](CommonMessage.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Last GPS updated successfully. |  -  |
| **401** | Unauthorized: Authentication required. |  -  |
| **404** | User not found. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## apiUploadBlogImagePost

> ApiUploadBlogImagePost200Response apiUploadBlogImagePost(apiUploadBlogImagePostRequest)

Upload a blog image and get back a URL

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiUploadBlogImagePostOperationRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // ApiUploadBlogImagePostRequest
    apiUploadBlogImagePostRequest: ...,
  } satisfies ApiUploadBlogImagePostOperationRequest;

  try {
    const data = await api.apiUploadBlogImagePost(body);
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
| **apiUploadBlogImagePostRequest** | [ApiUploadBlogImagePostRequest](ApiUploadBlogImagePostRequest.md) |  | |

### Return type

[**ApiUploadBlogImagePost200Response**](ApiUploadBlogImagePost200Response.md)

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

> CommonMessage apiUsernameVerifyPost(apiUsernameVerifyPostRequest)

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

[**CommonMessage**](CommonMessage.md)

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

> Blog apiViewBlogPost(blogID)

Details of one blog

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '';
import type { ApiViewBlogPostRequest } from '';

async function example() {
  console.log("🚀 Testing  SDK...");
  const api = new DefaultApi();

  const body = {
    // BlogID
    blogID: ...,
  } satisfies ApiViewBlogPostRequest;

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
| **blogID** | [BlogID](BlogID.md) |  | |

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

