import 'dart:math';
import 'config.dart';

import 'package:firebase_admob/firebase_admob.dart';

class InterAd {
  static final appId = Config.appId;
  static final adUnitId = Config.adUnitId;
  static final testDevices = Config.testDevices;
  static final test = false;

  static InterstitialAd _ad;

  static final targetInfo = MobileAdTargetingInfo(testDevices: testDevices);

  static init() {
    // Init AdMob with testId or the actual appId
    FirebaseAdMob.instance.initialize(
      appId: test ? FirebaseAdMob.testAppId : appId,
    );

    // Init ad with test value or the actual appUnitId and load it
    _ad = InterstitialAd(
      adUnitId: test ? InterstitialAd.testAdUnitId : adUnitId,
      targetingInfo: targetInfo,
    )..load();
  }

  static showAd() {
    var rng = Random();

    // 50% that an ad pops up
    if (50 > rng.nextInt(100))
      _ad..show(anchorOffset: 0.0, anchorType: AnchorType.bottom);
  }
}
