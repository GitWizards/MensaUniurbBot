import 'dart:math';

import 'package:firebase_admob/firebase_admob.dart';

class InterAd {
  static const appId = "ca-app-pub-8838692391489199~9266274568";
  static const adUnitId = "ca-app-pub-8838692391489199/5757434072";
  static const testDevices = ["CE744815682B17D9BF5B571E1F92478F"];
  static const test = false;

  static InterstitialAd _ad;

  static const MobileAdTargetingInfo targetInfo = MobileAdTargetingInfo(
    testDevices: testDevices,
  );

  static init() {
    FirebaseAdMob.instance.initialize(
      appId: test ? FirebaseAdMob.testAppId : appId,
    );

    _ad = InterstitialAd(
      adUnitId: test ? InterstitialAd.testAdUnitId : adUnitId,
      targetingInfo: targetInfo,
    )..load();
  }

  static showAd() {
    var rng = Random();

    // 50% that an Ad start
    if (50 > rng.nextInt(100))
      _ad..show(anchorOffset: 0.0, anchorType: AnchorType.bottom);
  }
}
