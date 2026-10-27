plugins { id("com.android.application") }
android {
    namespace = "local.tv.home"
    compileSdk = 34
    defaultConfig {
        applicationId = "local.mactv.home"
        minSdk = 21
        targetSdk = 34
        versionCode = 1
        versionName = "0.1.0"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
}
