import 'dart:ui';

import 'package:MensaUniurb/resultScreen.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:intl/intl.dart';
import 'package:dynamic_theme/dynamic_theme.dart';
import 'package:share/share.dart';
import 'package:url_launcher/url_launcher.dart';

import 'package:MensaUniurb/themes.dart';
import 'package:MensaUniurb/myWidgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

void main() async {
  // Lock app in portrait mode
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);

  // Load selected theme
  ThemeData theme = await Themes.load();

  // Run app
  runApp(MensaUniurb(theme: theme));
}

class MensaUniurb extends StatelessWidget {
  MensaUniurb({this.theme});

  // Appbar title
  final String title = "Mensa Uniurb";

  // Theme to be set
  final ThemeData theme;

  // Root of the application
  @override
  Widget build(BuildContext context) {
    return DynamicTheme(
      // Default theme
      data: (brightness) => theme,
      themedWidgetBuilder: (context, theme) {
        return MaterialApp(
          title: title,
          theme: theme,

          debugShowCheckedModeBanner: false,

          // Define application routes to various screens
          initialRoute: '/',
          routes: {
            '/': (context) => SearchScreen(title: title),
            '/results': (context) => ResultScreen(),
          },

          // Set locale stuff
          localizationsDelegates: [
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
          ],

          // Set italian as only locale
          supportedLocales: [Locale('it', 'IT')],
        );
      },
    );
  }
}

class SearchScreen extends StatefulWidget {
  // Constructor of the screen
  SearchScreen({Key key, this.title}) : super(key: key);

  // Title of the screen
  final String title;

  @override
  _SearchScreenState createState() => _SearchScreenState();
}

// Widget that creates the form search and send the query to the result widget
class _SearchScreenState extends State<SearchScreen> {
  // Variables that stores user choices for later use
  String kitchen = "duca";
  String date = DateFormat('MM-dd-yyyy').format(DateTime.now());
  String meal = "lunch";

  // Translates values from buttons to prettier form
  Map dict = {
    'duca': "Duca",
    'tridente': "Tridente",
    'lunch': "Pranzo",
    'dinner': "Cena",
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Top appbar with title
      appBar: AppBar(
        title: Text(widget.title, style: TextStyle(fontSize: 24)),
        centerTitle: true,
        // Makes the cool circle over appbar
        flexibleSpace: CustomPaint(
          painter: CircleAppBar(context: context),
          child: Container(padding: EdgeInsets.only(top: 80.0)),
        ),
      ),

      // Body of the screen
      body: Container(
        padding: EdgeInsets.only(top: 90),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Container(
              padding: EdgeInsets.only(top: 12, bottom: 12),
              // Custom radio buttons
              child: RadioButtons(
                textButton1: "Duca",
                valueButton1: "duca",
                textButton2: "Tridente",
                valueButton2: "tridente",
                setFunc: _setKitchen,
              ),
            ),
            // Custom radio buttons
            Container(
              padding: EdgeInsets.only(top: 12, bottom: 12),
              child: RadioButtons(
                textButton1: "Pranzo",
                valueButton1: "lunch",
                textButton2: "Cena",
                valueButton2: "dinner",
                setFunc: _setMeal,
              ),
            ),
            // Custom data picker
            Container(
              padding: EdgeInsets.only(top: 12, bottom: 12),
              child: DataPicker(
                setFunc: _setDate,
              ),
            ),
          ],
        ),
      ),

      // Button to start query
      floatingActionButton: FloatingActionButton.extended(
        label: Text("Cerca"),
        icon: Icon(Icons.search),
        onPressed: () {
          // Translates values from buttons to prettier form
          String kName = dict['$kitchen'];
          String mName = dict['$meal'];

          // Navigate to ResultScreen when tapped
          Navigator.pushNamed(
            context,
            '/results',
            arguments: SearchArguments(
              title: "$kName - $mName",
              kitchen: kitchen,
              date: date,
              meal: meal,
            ),
          );
        },
      ),

      // Drawer on the left
      drawer: Container(
        width: 250,
        color: Theme.of(context).backgroundColor,
        child: ListView(
          children: <Widget>[
            ListTile(
              leading: Icon(FontAwesomeIcons.palette),
              title: Text('Tema', style: TextStyle(fontSize: 17)),
            ),

            // Themes selection
            Row(
              children: <Widget>[
                IconButton(
                  icon: CircleAvatar(backgroundColor: Colors.blue),
                  onPressed: () => applyTheme('blue'),
                ),
                IconButton(
                  icon: CircleAvatar(backgroundColor: Colors.green),
                  onPressed: () => applyTheme('green'),
                ),
                IconButton(
                  icon: CircleAvatar(backgroundColor: Colors.red),
                  onPressed: () => applyTheme('red'),
                ),
              ],
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            ),

            Divider(),

            // Mail to devs
            ListTile(
              leading: Icon(Icons.mail),
              title: Text('Email', style: TextStyle(fontSize: 17)),
              onTap: () => _launchURL("mailto:dawid.weglarz95@gmail.com"),
            ),

            // Open github repo
            ListTile(
              leading: Icon(FontAwesomeIcons.github),
              title: Text('Github', style: TextStyle(fontSize: 17)),
              onTap: () =>
                  _launchURL("https://github.com/FastRadeox/MensaUniurbBot"),
            ),

            // Open paypal.me page
            ListTile(
              leading: Icon(FontAwesomeIcons.paypal),
              title: Text('Donazioni', style: TextStyle(fontSize: 17)),
              onTap: () => _launchURL("https://www.paypal.me/Radeox"),
            ),

            // Share google play link
            ListTile(
              leading: Icon(FontAwesomeIcons.googlePlay),
              title: Text('Condividi', style: TextStyle(fontSize: 17)),
              onTap: () => Share.share(
                  "https://play.google.com/store/apps/details?id=com.radeox.mensa_uniurb"),
            ),

            // Open telegram bot page
            ListTile(
              leading: Icon(FontAwesomeIcons.telegramPlane),
              title: Text('Bot Telegram', style: TextStyle(fontSize: 17)),
              onTap: () => _launchURL("https://t.me/MensaUniurb_Bot"),
            ),
          ],
        ),
      ),
    );
  }

  // Function to apply and save the selected theme
  applyTheme(theme) {
    // Check and update theme
    setState(() {
      switch (theme) {
        case 'blue':
          DynamicTheme.of(context).setThemeData(Themes.blue());
          break;
        case 'green':
          DynamicTheme.of(context).setThemeData(Themes.green());
          break;
        case 'red':
          DynamicTheme.of(context).setThemeData(Themes.red());
          break;
      }
    });

    // Save selected theme
    Themes.save(theme);

    // Close the drawer
    Navigator.pop(context);
  }

  // Function called from child widgets to set the value
  _setKitchen(value) => kitchen = value;

  // Function called from child widgets to set the value
  _setDate(value) => date = value;

  // Function called from child widgets to set the value
  _setMeal(value) => meal = value;

  // Open URL in browser
  _launchURL(url) async {
    // Check if can launch URL
    if (await canLaunch(url))
      await launch(url);
    else
      throw 'Could not launch $url';

    // Close the drawer
    Navigator.pop(context);
  }
}

// Custom painter that creates the blue circle over the appBar
class CircleAppBar extends CustomPainter {
  CircleAppBar({this.context});

  final BuildContext context;

  @override
  void paint(Canvas canvas, Size size) {
    // Create painter
    final paint = Paint();

    // Set the color based of accent
    paint.color = Theme.of(context).accentColor;

    // Compute the center where the circle should be drawn
    Offset center = Offset(size.width * 0.5, 0);

    // Draw the circle
    canvas.drawCircle(center, size.width * 0.7, paint);
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => true;
}
