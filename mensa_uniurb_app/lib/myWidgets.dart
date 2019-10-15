import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:intl/intl.dart';

// Class that encapsulate a new button with a
// date text and a dataPicker
class DataPicker extends StatefulWidget {
  // Constructor
  DataPicker({Key key, this.setFunc}) : super(key: key);

  // The 'setFunc' is the function used to set a variable in the parent widget
  final Function setFunc;

  @override
  _DataPickerState createState() => _DataPickerState();
}

// Class that encapsulate a new button with a
// date text and a dataPicker
class _DataPickerState extends State<DataPicker> {
  String date = DateFormat('dd/MM/yyyy').format(DateTime.now());

  @override
  Widget build(BuildContext context) {
    return Container(
      child: RaisedButton(
        child: Row(
          children: <Widget>[
            Container(
              padding: EdgeInsets.all(7),
              child: Text(
                date,
                style: TextStyle(
                  fontSize: MediaQuery.of(context).size.width * 0.07,
                  color: Colors.white,
                  shadows: <Shadow>[
                    Shadow(
                      color: Colors.black54,
                      offset: Offset(2.0, 2.0),
                      blurRadius: 5.0,
                    )
                  ],
                ),
              ),
            ),
            Container(
              child: Icon(
                Icons.date_range,
                color: Colors.white,
              ),
            ),
          ],
          mainAxisAlignment: MainAxisAlignment.center,
        ),
        shape: StadiumBorder(),
        color: Theme.of(context).accentColor,
        disabledColor: Colors.grey,
        onPressed: () => _showDateTimePicker(context),
      ),
      width: MediaQuery.of(context).size.width * 0.85,
      height: MediaQuery.of(context).size.height * 0.09,
    );
  }

  // Shows the dataPicker to select a date
  _showDateTimePicker(BuildContext context) async {
    DateTime selected;
    DateTime today = DateTime.now();
    Duration week = Duration(days: 7);

    // Get selected date
    selected = await showDatePicker(
      context: context,
      initialDate: today,
      firstDate: today,
      lastDate: today.add(week),
    );

    // Update the state and call the 'setFunc'
    setState(() {
      if (selected != null) {
        date = DateFormat('dd/MM/yyyy').format(selected);
        widget.setFunc(DateFormat('MM-dd-yyyy').format(selected));
      }
    });
  }
}

// Class that encapsulates two buttons as a pair of radio buttons
class RadioButtons extends StatefulWidget {
  // The constructor requires the text and the value of the two buttons
  RadioButtons({
    Key key,
    this.textButton1,
    this.valueButton1,
    this.textButton2,
    this.valueButton2,
    this.setFunc,
  }) : super(key: key);

  // Texts of the buttons
  final String textButton1;
  final String textButton2;

  // Buttons values
  final String valueButton1;
  final String valueButton2;

  // The 'setFunc' is the function used to set a variable in the parent widget
  final Function setFunc;

  @override
  _RadioButtonsState createState() => _RadioButtonsState();
}

// Class that encapsulates two buttons as a pair of radio buttons
class _RadioButtonsState extends State<RadioButtons> {
  // Ensure only one button is active at given time
  bool selected = true;

  @override
  Widget build(BuildContext context) {
    return Row(
      // Create the two buttons
      children: <Widget>[
        _singleButton(
          context,
          widget.textButton1,
          widget.valueButton1,
          selected,
        ),
        _singleButton(
          context,
          widget.textButton2,
          widget.valueButton2,
          !selected,
        ),
      ],
      mainAxisAlignment: MainAxisAlignment.center,
    );
  }

  // Generate a single button
  Widget _singleButton(context, text, value, active) {
    return Container(
      padding: EdgeInsets.only(left: 8, right: 8),
      child: Container(
        child: RaisedButton(
          child: Text(
            text,
            style: TextStyle(
              fontSize: MediaQuery.of(context).size.width * 0.07,
              color: Colors.white,
              shadows: <Shadow>[
                Shadow(
                  color: Colors.black54,
                  offset: Offset(2.0, 2.0),
                  blurRadius: 5.0,
                )
              ],
            ),
          ),
          shape: StadiumBorder(),
          color: Colors.grey,
          disabledColor: Theme.of(context).accentColor,

          // Check if the buttons is active and take action
          onPressed: active ? null : () => _changeActiveButton(),
        ),
        width: MediaQuery.of(context).size.width * 0.4,
        height: MediaQuery.of(context).size.height * 0.08,
      ),
    );
  }

  // Change the active button and call the 'setFunc' from the parend widget
  _changeActiveButton() {
    setState(() {
      // Change active button value
      selected = !selected;

      // Based on which button is active set a value
      if (selected)
        widget.setFunc(widget.valueButton1);
      else
        widget.setFunc(widget.valueButton2);
    });
  }
}
