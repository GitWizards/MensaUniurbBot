import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:http/http.dart';

import 'ads.dart';

class ResultScreen extends StatefulWidget {
  // Constructor of the screen
  ResultScreen({Key key, this.title}) : super(key: key);

  // Title of the screen
  final String title;

  @override
  _ResultScreenState createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  // Flag to check if data has been already requested
  bool needData = true;

  // Arguments of the search
  SearchArguments args;

  // Future list of widgets that will be made in the getList function
  Future<List<Widget>> results;

  @override
  Widget build(BuildContext context) {
    if (needData) {
      // Extract arguments passed from the search screen
      args = ModalRoute.of(context).settings.arguments;
      results = getList(args);

      // Set flag to false
      needData = false;
    }

    // Dipslay interstitial ad
    InterAd.showAd();

    return Scaffold(
      appBar: AppBar(title: Text("${args.title}")),
      body: FutureBuilder(
        future: results,
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
              return Column(
                children: <Widget>[
                  Expanded(
                    child: ListView(children: content),
                  ),
                ],
              );
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
                        style: TextStyle(fontSize: 20),
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
          list.add(
            Card(
              child: ListTile(
                title: Text('$item'),
                subtitle: Text('$infos'),
              ),
            ),
          );
        } else {
          // Otherwise add it without anything
          list.add(Card(
            child: ListTile(
              title: Text('$item'),
            ),
          ));
        }
      }
    }

    return list;
  }

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
