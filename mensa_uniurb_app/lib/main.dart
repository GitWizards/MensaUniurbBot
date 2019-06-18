import 'dart:convert';
import 'dart:ui';

import 'package:MensaUniurb/ads.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart';
import 'package:intl/intl.dart';
import 'package:dynamic_theme/dynamic_theme.dart';
import 'package:url_launcher/url_launcher.dart';

import 'package:MensaUniurb/themes.dart';
import 'package:MensaUniurb/myWidgets.dart';

void main() async {
  // Initialize interstitial ad
  InterAd.init();

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

          // Define application routes to various screens
          initialRoute: '/',
          routes: {
            '/': (context) => SearchScreen(title: title),
            '/results': (context) => ResultScreen(),
          },
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
          child: Padding(padding: const EdgeInsets.only(top: 80.0)),
        ),
      ),

      // Body of the screen
      body: Padding(
        padding: const EdgeInsets.only(top: 70.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Padding(
              padding: const EdgeInsets.all(8.0),
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
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: RadioButtons(
                textButton1: "Pranzo",
                valueButton1: "lunch",
                textButton2: "Cena",
                valueButton2: "dinner",
                setFunc: _setMeal,
              ),
            ),
            // Custom data picker
            Padding(
              padding: const EdgeInsets.all(8.0),
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
              leading: Icon(Icons.brightness_6),
              title: Text(
                'Theme',
                style: TextStyle(fontSize: 17),
              ),
            ),
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
                  icon: CircleAvatar(backgroundColor: Colors.teal),
                  onPressed: () => applyTheme('teal'),
                ),
              ],
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            ),
            ListTile(
              leading: Icon(Icons.message),
              title: Text('Bot Telegram', style: TextStyle(fontSize: 17)),
              onTap: () => _launchURL("https://t.me/MensaUniurb_Bot"),
            ),
            ListTile(
              leading: Icon(Icons.person),
              title: Text('Contact us', style: TextStyle(fontSize: 17)),
              onTap: () => _launchURL("https://t.me/Radeox"),
            ),
            ListTile(
              leading: Icon(Icons.monetization_on),
              title: Text('Donazioni', style: TextStyle(fontSize: 17)),
              onTap: () => _launchURL("https://www.paypal.me/Radeox"),
            ),
            // ListTile(
            //   leading: Icon(Icons.info),
            //   title: Text('Info', style: TextStyle(fontSize: 17)),
            //   onTap: () => print("info"),
            // ),
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
        case 'teal':
          DynamicTheme.of(context).setThemeData(Themes.teal());
          break;
      }
    });

    // Save selected theme
    Themes.save(theme);

    // Close the drawer
    Navigator.pop(context);
  }

  // Function called from child widgets to set the value
  _setKitchen(value) {
    kitchen = value;
  }

  // Function called from child widgets to set the value
  _setDate(value) {
    date = value;
  }

  // Function called from child widgets to set the value
  _setMeal(value) {
    meal = value;
  }

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

class ResultScreen extends StatelessWidget {
  // Constructor of the screen
  ResultScreen({Key key, this.title}) : super(key: key);

  // Title of the screen
  final String title;

  @override
  Widget build(BuildContext context) {
    // Extract arguments passed from the search screen
    final SearchArguments args = ModalRoute.of(context).settings.arguments;

    // Dipslay interstitial ad
    InterAd.showAd();

    return Scaffold(
      appBar: AppBar(title: Text("${args.title}")),
      body: FutureBuilder(
        future: getList(args),
        builder: (BuildContext context, AsyncSnapshot<List> snapshot) {
          if (!snapshot.hasData) {
            // Display during loading
            return Center(
              // Loading animation
              child: CircularProgressIndicator(),
            );
          } else {
            List content = snapshot.data;

            // If some content exists
            if (content.isNotEmpty) {
              // Create and return the list
              return Column(children: <Widget>[
                Expanded(child: ListView(children: content)),
              ]);
            } else {
              // If the result is empty display alert
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: <Widget>[
                    Icon(
                      Icons.error,
                      size: 100,
                      color: Colors.red,
                    ),
                    Text(
                      "Ops!",
                      style: TextStyle(fontSize: 50),
                    ),
                    Padding(
                      padding: const EdgeInsets.only(
                        top: 10,
                        left: 40,
                        right: 40,
                      ),
                      child: Text(
                        "Sembra che la mensa sia chiusa.",
                        style: TextStyle(
                          fontSize: 20,
                        ),
                      ),
                    ),
                  ],
                ),
              );
            }
          }
        },
      ),
    );
  }

  // Create a list from the result
  Future<List<Widget>> getList(SearchArguments args) async {
    // Result of the request to API
    Map result = {};

    // Create an empty list
    List<Widget> list = List();

    Map names = {
      'first': "Primi",
      'second': "Secondi",
      'side': "Contorno",
      'fruit': "Frutta",
    };

    // Make the url with the arguments from the previous screen
    String url =
        'http://51.158.173.57:9543/${args.kitchen}/${args.date}/${args.meal}';

    // Send the request
    Response response = await get(url);

    // Try decoding results
    // If they are empty the result will not be a JSON
    try {
      result = json.decode(response.body);
    } on Exception {}

    // If no results (network/request error) or the
    //results are empty (closing day) then return the empty list
    if ((result.isEmpty) || (result['menu']['first'].isEmpty)) return list;

    // Loop through keys of the json
    for (String type in result['menu'].keys) {
      list.add(namedSpacer('${names[type]}'));

      // Loop through each item and add them to list
      for (String item in result['menu'][type]) {
        // Extract last part of the string
        String infos = item.split(" ").removeLast();

        // Check if it contains allergry infos
        RegExp filter = RegExp('([1-9])');

        if (filter.hasMatch(infos)) {
          // Remove them from the original string
          // and add them as subtitle
          item = item.replaceAll(infos, '');
          infos = infos.toUpperCase();

          // Add the item to the list with subtitle
          list.add(Card(
            child: ListTile(
              title: Text('$item'),
              subtitle: Text('$infos'),
            ),
          ));
        } else {
          // Otherwise add it without anything
          list.add(Card(
            child: ListTile(title: Text('$item')),
          ));
        }
      }
    }

    return list;
  }

  // Custom widget - Spacer with name and icon
  Widget namedSpacer(value, {icon = Icons.local_dining}) {
    return Row(
      children: <Widget>[
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: Icon(icon),
        ),
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: Text(value, style: TextStyle(fontSize: 25)),
        ),
      ],
      mainAxisAlignment: MainAxisAlignment.center,
      crossAxisAlignment: CrossAxisAlignment.center,
    );
  }
}

// Class that incapsulates the arguments required for the search query
class SearchArguments {
  // Constructor of the arguments
  SearchArguments({
    this.title,
    @required this.kitchen,
    @required this.date,
    @required this.meal,
  });

  // Kitchen name
  final String title;

  // Kitchen name
  final String kitchen;

  // Date in MM-DD-YYYY format
  final String date;

  // Meal (lunch or dinner)
  final String meal;
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
    Offset center = Offset(size.width / 2, size.height * 0.1);

    // Draw the circle
    canvas.drawCircle(center, 250, paint);
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => true;
}
