/**
 * The $1 Unistroke Recognizer (JavaScript version)
 *
 *	Jacob O. Wobbrock, Ph.D.
 * 	The Information School
 *	University of Washington
 *	Seattle, WA 98195-2840
 *	wobbrock@uw.edu
 *
 *	Andrew D. Wilson, Ph.D.
 *	Microsoft Research
 *	One Microsoft Way
 *	Redmond, WA 98052
 *	awilson@microsoft.com
 *
 *	Yang Li, Ph.D.
 *	Department of Computer Science and Engineering
 * 	University of Washington
 *	Seattle, WA 98195-2840
 * 	yangli@cs.washington.edu
 *
 * The academic publication for the $1 recognizer, and what should be 
 * used to cite it, is:
 *
 *	Wobbrock, J.O., Wilson, A.D. and Li, Y. (2007). Gestures without 
 *	  libraries, toolkits or training: A $1 recognizer for user interface 
 *	  prototypes. Proceedings of the ACM Symposium on User Interface 
 *	  Software and Technology (UIST '07). Newport, Rhode Island (October 
 *	  7-10, 2007). New York: ACM Press, pp. 159-168.
 *
 * The Protractor enhancement was separately published by Yang Li and programmed 
 * here by Jacob O. Wobbrock:
 *
 *	Li, Y. (2010). Protractor: A fast and accurate gesture
 *	  recognizer. Proceedings of the ACM Conference on Human
 *	  Factors in Computing Systems (CHI '10). Atlanta, Georgia
 *	  (April 10-15, 2010). New York: ACM Press, pp. 2169-2172.
 *
 * This software is distributed under the "New BSD License" agreement:
 *
 * Copyright (C) 2007-2012, Jacob O. Wobbrock, Andrew D. Wilson and Yang Li.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *    * Redistributions of source code must retain the above copyright
 *      notice, this list of conditions and the following disclaimer.
 *    * Redistributions in binary form must reproduce the above copyright
 *      notice, this list of conditions and the following disclaimer in the
 *      documentation and/or other materials provided with the distribution.
 *    * Neither the names of the University of Washington nor Microsoft,
 *      nor the names of its contributors may be used to endorse or promote
 *      products derived from this software without specific prior written
 *      permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Jacob O. Wobbrock OR Andrew D. Wilson
 * OR Yang Li BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
 * OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
**/
//
// Point class
//
function Point(x, y) // constructor
{
	this.X = x;
	this.Y = y;
}
//
// Rectangle class
//
function Rectangle(x, y, width, height) // constructor
{
	this.X = x;
	this.Y = y;
	this.Width = width;
	this.Height = height;
}
//
// Unistroke class: a unistroke template
//
function Unistroke(name, points) // constructor
{
	this.Name = name;
	this.Points = Resample(points, NumPoints);
	var radians = IndicativeAngle(this.Points);
	this.Points = RotateBy(this.Points, -radians);
	this.Points = ScaleTo(this.Points, SquareSize);
	this.Points = TranslateTo(this.Points, Origin);
	this.Vector = Vectorize(this.Points); // for Protractor
}
//
// Result class
//
function Result(name, score) // constructor
{
	this.Name = name;
	this.Score = score;
}
//
// DollarRecognizer class constants
//
var NumPoints = 64;
var SquareSize = 250.0;
var Origin = new Point(0,0);
var Diagonal = Math.sqrt(SquareSize * SquareSize + SquareSize * SquareSize);
var HalfDiagonal = 0.5 * Diagonal;
var AngleRange = Deg2Rad(45.0);
var AnglePrecision = Deg2Rad(2.0);
var Phi = 0.5 * (-1.0 + Math.sqrt(5.0)); // Golden Ratio
//
// DollarRecognizer class
//
function DollarRecognizer() // constructor
{
	//
	// one built-in unistroke per gesture type
	//
	this.Unistrokes = [];
	//this.Unistrokes.push(new Unistroke("axis-topleft", new Array(new Point(317,-325),new Point(317,-325),new Point(316,-325),new Point(314,-325),new Point(310,-325),new Point(304,-325),new Point(298,-325),new Point(289,-325),new Point(278,-325),new Point(268,-325),new Point(253,-325),new Point(240,-325),new Point(227,-325),new Point(210,-325),new Point(197,-325),new Point(185,-328),new Point(175,-329),new Point(165,-330),new Point(156,-332),new Point(151,-333),new Point(145,-334),new Point(142,-334),new Point(138,-334),new Point(135,-334),new Point(133,-334),new Point(131,-335),new Point(128,-335),new Point(124,-337),new Point(120,-337),new Point(115,-338),new Point(110,-338),new Point(103,-339),new Point(97,-339),new Point(92,-341),new Point(87,-343),new Point(84,-343),new Point(81,-344),new Point(80,-344),new Point(80,-343),new Point(79,-339),new Point(79,-335),new Point(79,-328),new Point(79,-319),new Point(79,-307),new Point(79,-292),new Point(79,-276),new Point(79,-254),new Point(79,-235),new Point(79,-213),new Point(79,-191),new Point(79,-169),new Point(79,-145),new Point(79,-126),new Point(79,-111),new Point(79,-97),new Point(79,-86),new Point(79,-74),new Point(79,-63),new Point(78,-54),new Point(77,-46),new Point(77,-39),new Point(77,-34),new Point(75,-30),new Point(75,-27))));
	//this.Unistrokes.push(new Unistroke("axis-topright", new Array(new Point(47,-329),new Point(47,-329),new Point(50,-329),new Point(61,-329),new Point(72,-328),new Point(85,-326),new Point(101,-326),new Point(120,-326),new Point(143,-324),new Point(168,-324),new Point(194,-320),new Point(218,-320),new Point(243,-320),new Point(265,-320),new Point(285,-319),new Point(299,-319),new Point(310,-319),new Point(317,-318),new Point(325,-318),new Point(330,-318),new Point(333,-318),new Point(335,-318),new Point(336,-318),new Point(337,-318),new Point(337,-316),new Point(337,-312),new Point(337,-305),new Point(337,-296),new Point(337,-282),new Point(337,-269),new Point(337,-253),new Point(337,-231),new Point(337,-207),new Point(337,-179),new Point(337,-155),new Point(337,-133),new Point(337,-111),new Point(337,-99),new Point(337,-87),new Point(337,-74),new Point(337,-65),new Point(337,-57),new Point(337,-51),new Point(337,-49),new Point(337,-48))));
	this.Unistrokes.push(new Unistroke("Axis", new Array(new Point(81,-493),new Point(80,-491),new Point(80,-483),new Point(80,-473),new Point(80,-463),new Point(80,-450),new Point(80,-433),new Point(80,-412),new Point(80,-390),new Point(80,-371),new Point(80,-354),new Point(80,-340),new Point(80,-326),new Point(80,-310),new Point(80,-300),new Point(80,-288),new Point(80,-278),new Point(80,-272),new Point(80,-265),new Point(80,-261),new Point(80,-259),new Point(80,-257),new Point(82,-257),new Point(91,-257),new Point(103,-258),new Point(128,-261),new Point(158,-261),new Point(198,-261),new Point(247,-261),new Point(285,-261),new Point(320,-261),new Point(347,-261),new Point(364,-261),new Point(376,-261),new Point(383,-261),new Point(386,-261))));
	//this.Unistrokes.push(new Unistroke("axis-bottomright", new Array(new Point(322,-382),new Point(322,-378),new Point(322,-373),new Point(322,-348),new Point(322,-338),new Point(322,-326),new Point(322,-314),new Point(322,-302),new Point(322,-293),new Point(323,-279),new Point(325,-272),new Point(326,-260),new Point(329,-250),new Point(329,-242),new Point(329,-237),new Point(329,-233),new Point(330,-226),new Point(331,-220),new Point(332,-214),new Point(332,-211),new Point(332,-209),new Point(332,-207),new Point(332,-206),new Point(332,-205),new Point(332,-204),new Point(332,-203),new Point(332,-200),new Point(332,-197),new Point(332,-194),new Point(332,-190),new Point(332,-185),new Point(332,-181),new Point(332,-175),new Point(332,-170),new Point(332,-167),new Point(332,-165),new Point(332,-163),new Point(332,-162),new Point(332,-161),new Point(332,-160),new Point(330,-160),new Point(328,-160),new Point(322,-160),new Point(314,-160),new Point(303,-160),new Point(287,-160),new Point(268,-160),new Point(243,-160),new Point(218,-160),new Point(188,-159),new Point(161,-159),new Point(138,-157),new Point(122,-157),new Point(107,-157),new Point(97,-157),new Point(91,-157),new Point(88,-157),new Point(87,-157),new Point(85,-157),new Point(84,-157),new Point(83,-157))));
	
	this.Unistrokes.push(new Unistroke("Legend", new Array(new Point(302,-381),new Point(300,-381),new Point(298,-381),new Point(296,-381),new Point(293,-381),new Point(289,-382),new Point(285,-382),new Point(279,-383),new Point(274,-383),new Point(266,-383),new Point(258,-383),new Point(248,-383),new Point(239,-383),new Point(230,-383),new Point(220,-387),new Point(212,-387),new Point(203,-387),new Point(197,-387),new Point(189,-388),new Point(182,-388),new Point(177,-388),new Point(170,-388),new Point(164,-390),new Point(159,-390),new Point(152,-390),new Point(148,-390),new Point(144,-390),new Point(140,-390),new Point(138,-390),new Point(134,-390),new Point(130,-390),new Point(127,-390),new Point(124,-390),new Point(121,-390),new Point(118,-390),new Point(116,-390),new Point(115,-390),new Point(112,-390),new Point(110,-390),new Point(109,-390),new Point(107,-390),new Point(107,-389),new Point(107,-388),new Point(107,-384),new Point(107,-381),new Point(107,-377),new Point(107,-371),new Point(107,-367),new Point(107,-360),new Point(107,-354),new Point(107,-348),new Point(107,-340),new Point(107,-333),new Point(107,-324),new Point(107,-319),new Point(107,-311),new Point(107,-304),new Point(107,-295),new Point(107,-290),new Point(107,-285),new Point(107,-280),new Point(107,-277),new Point(107,-273),new Point(107,-269),new Point(107,-266),new Point(107,-260),new Point(107,-256),new Point(107,-252),new Point(107,-249),new Point(107,-245),new Point(107,-242),new Point(107,-240),new Point(107,-237),new Point(107,-234),new Point(107,-231),new Point(107,-228),new Point(107,-227),new Point(107,-224),new Point(107,-223),new Point(107,-220),new Point(107,-219),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-218),new Point(107,-217),new Point(108,-217),new Point(108,-217),new Point(109,-217),new Point(116,-218),new Point(116,-218),new Point(120,-218),new Point(133,-219),new Point(133,-219),new Point(133,-219),new Point(139,-219),new Point(146,-219),new Point(146,-219),new Point(153,-221),new Point(160,-221),new Point(166,-221),new Point(166,-221),new Point(174,-221),new Point(192,-221),new Point(192,-221),new Point(192,-221),new Point(201,-221),new Point(201,-221),new Point(212,-221),new Point(230,-221),new Point(230,-221),new Point(238,-221),new Point(245,-221),new Point(245,-221),new Point(252,-221),new Point(265,-222),new Point(265,-222),new Point(270,-222),new Point(270,-222),new Point(278,-222),new Point(278,-222),new Point(282,-222),new Point(283,-223),new Point(283,-223),new Point(285,-223),new Point(288,-223),new Point(288,-223),new Point(289,-223),new Point(289,-223),new Point(289,-223),new Point(290,-223),new Point(290,-223),new Point(291,-223),new Point(291,-223),new Point(292,-223),new Point(293,-223),new Point(293,-223),new Point(295,-223),new Point(295,-223),new Point(295,-223),new Point(295,-223),new Point(295,-223),new Point(295,-223),new Point(296,-225),new Point(296,-229),new Point(296,-233),new Point(296,-240),new Point(296,-246),new Point(296,-252),new Point(296,-260),new Point(296,-268),new Point(295,-279),new Point(294,-286),new Point(293,-295),new Point(292,-304),new Point(292,-309),new Point(289,-319),new Point(288,-329),new Point(287,-337),new Point(286,-345),new Point(284,-353),new Point(283,-359),new Point(282,-361),new Point(280,-364),new Point(279,-367),new Point(279,-370),new Point(279,-372),new Point(278,-375),new Point(278,-376),new Point(278,-377),new Point(278,-378),new Point(278,-380),new Point(276,-382),new Point(276,-384),new Point(276,-385),new Point(276,-387),new Point(276,-389),new Point(276,-391),new Point(276,-392),new Point(276,-394),new Point(275,-396),new Point(275,-397),new Point(275,-398))));

	//
	// The $1 Gesture Recognizer API begins here -- 3 methods: Recognize(), AddGesture(), and DeleteUserGestures()
	//
	this.Recognize = function(points, useProtractor)
	{
		points = Resample(points, NumPoints);
		var radians = IndicativeAngle(points);
		points = RotateBy(points, -radians);
		points = ScaleTo(points, SquareSize);
		points = TranslateTo(points, Origin);
		var vector = Vectorize(points); // for Protractor

		var b = +Infinity;
		var u = -1;
		for (var i = 0; i < this.Unistrokes.length; i++) // for each unistroke
		{
			var d;
			if (useProtractor) // for Protractor
				d = OptimalCosineDistance(this.Unistrokes[i].Vector, vector);
			else // Golden Section Search (original $1)
				d = DistanceAtBestAngle(points, this.Unistrokes[i], -AngleRange, +AngleRange, AnglePrecision);
			if (d < b) {
				b = d; // best (least) distance
				u = i; // unistroke
			}
		}
		return (u == -1) ? new Result("No match.", 0.0) : new Result(this.Unistrokes[u].Name, useProtractor ? 1.0 / b : 1.0 - b / HalfDiagonal);
	};
	this.AddGesture = function(name, points)
	{
		this.Unistrokes[this.Unistrokes.length] = new Unistroke(name, points); // append new unistroke
		var num = 0;
		for (var i = 0; i < this.Unistrokes.length; i++) {
			if (this.Unistrokes[i].Name == name)
				num++;
		}
		return num;
	}
	this.DeleteUserGestures = function()
	{
		this.Unistrokes.length = NumUnistrokes; // clear any beyond the original set
		return NumUnistrokes;
	}
}
//
// Private helper functions from this point down
//
function Resample(points, n)
{
	var I = PathLength(points) / (n - 1); // interval length
	var D = 0.0;
	var newpoints = new Array(points[0]);
	for (var i = 1; i < points.length; i++)
	{
		var d = Distance(points[i - 1], points[i]);
		if ((D + d) >= I)
		{
			var qx = points[i - 1].X + ((I - D) / d) * (points[i].X - points[i - 1].X);
			var qy = points[i - 1].Y + ((I - D) / d) * (points[i].Y - points[i - 1].Y);
			var q = new Point(qx, qy);
			newpoints[newpoints.length] = q; // append new point 'q'
			points.splice(i, 0, q); // insert 'q' at position i in points s.t. 'q' will be the next i
			D = 0.0;
		}
		else D += d;
	}
	if (newpoints.length == n - 1) // somtimes we fall a rounding-error short of adding the last point, so add it if so
		newpoints[newpoints.length] = new Point(points[points.length - 1].X, points[points.length - 1].Y);
	return newpoints;
}
function IndicativeAngle(points)
{
	var c = Centroid(points);
	return Math.atan2(c.Y - points[0].Y, c.X - points[0].X);
}
function RotateBy(points, radians) // rotates points around centroid
{
	var c = Centroid(points);
	var cos = Math.cos(radians);
	var sin = Math.sin(radians);
	var newpoints = new Array();
	for (var i = 0; i < points.length; i++) {
		var qx = (points[i].X - c.X) * cos - (points[i].Y - c.Y) * sin + c.X
		var qy = (points[i].X - c.X) * sin + (points[i].Y - c.Y) * cos + c.Y;
		newpoints[newpoints.length] = new Point(qx, qy);
	}
	return newpoints;
}
function ScaleTo(points, size) // non-uniform scale; assumes 2D gestures (i.e., no lines)
{
	var B = BoundingBox(points);
	var newpoints = new Array();
	for (var i = 0; i < points.length; i++) {
		var qx = points[i].X * (size / B.Width);
		var qy = points[i].Y * (size / B.Height);
		newpoints[newpoints.length] = new Point(qx, qy);
	}
	return newpoints;
}
function TranslateTo(points, pt) // translates points' centroid
{
	var c = Centroid(points);
	var newpoints = new Array();
	for (var i = 0; i < points.length; i++) {
		var qx = points[i].X + pt.X - c.X;
		var qy = points[i].Y + pt.Y - c.Y;
		newpoints[newpoints.length] = new Point(qx, qy);
	}
	return newpoints;
}
function Vectorize(points) // for Protractor
{
	var sum = 0.0;
	var vector = new Array();
	for (var i = 0; i < points.length; i++) {
		vector[vector.length] = points[i].X;
		vector[vector.length] = points[i].Y;
		sum += points[i].X * points[i].X + points[i].Y * points[i].Y;
	}
	var magnitude = Math.sqrt(sum);
	for (var i = 0; i < vector.length; i++)
		vector[i] /= magnitude;
	return vector;
}
function OptimalCosineDistance(v1, v2) // for Protractor
{
	var a = 0.0;
	var b = 0.0;
	for (var i = 0; i < v1.length; i += 2) {
		a += v1[i] * v2[i] + v1[i + 1] * v2[i + 1];
                b += v1[i] * v2[i + 1] - v1[i + 1] * v2[i];
	}
	var angle = Math.atan(b / a);
	return Math.acos(a * Math.cos(angle) + b * Math.sin(angle));
}
function DistanceAtBestAngle(points, T, a, b, threshold)
{
	var x1 = Phi * a + (1.0 - Phi) * b;
	var f1 = DistanceAtAngle(points, T, x1);
	var x2 = (1.0 - Phi) * a + Phi * b;
	var f2 = DistanceAtAngle(points, T, x2);
	while (Math.abs(b - a) > threshold)
	{
		if (f1 < f2) {
			b = x2;
			x2 = x1;
			f2 = f1;
			x1 = Phi * a + (1.0 - Phi) * b;
			f1 = DistanceAtAngle(points, T, x1);
		} else {
			a = x1;
			x1 = x2;
			f1 = f2;
			x2 = (1.0 - Phi) * a + Phi * b;
			f2 = DistanceAtAngle(points, T, x2);
		}
	}
	return Math.min(f1, f2);
}
function DistanceAtAngle(points, T, radians)
{
	var newpoints = RotateBy(points, radians);
	return PathDistance(newpoints, T.Points);
}
function Centroid(points)
{
	var x = 0.0, y = 0.0;
	for (var i = 0; i < points.length; i++) {
		x += points[i].X;
		y += points[i].Y;
	}
	x /= points.length;
	y /= points.length;
	return new Point(x, y);
}
function BoundingBox(points)
{
	var minX = +Infinity, maxX = -Infinity, minY = +Infinity, maxY = -Infinity;
	for (var i = 0; i < points.length; i++) {
		minX = Math.min(minX, points[i].X);
		minY = Math.min(minY, points[i].Y);
		maxX = Math.max(maxX, points[i].X);
		maxY = Math.max(maxY, points[i].Y);
	}
	return new Rectangle(minX, minY, maxX - minX, maxY - minY);
}
function PathDistance(pts1, pts2)
{
	var d = 0.0;
	for (var i = 0; i < pts1.length; i++) // assumes pts1.length == pts2.length
		d += Distance(pts1[i], pts2[i]);
	return d / pts1.length;
}
function PathLength(points)
{
	var d = 0.0;
	for (var i = 1; i < points.length; i++)
		d += Distance(points[i - 1], points[i]);
	return d;
}
function Distance(p1, p2)
{
	var dx = p2.X - p1.X;
	var dy = p2.Y - p1.Y;
	return Math.sqrt(dx * dx + dy * dy);
}
function Deg2Rad(d) { return (d * Math.PI / 180.0); }