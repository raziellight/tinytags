# Introduction

Do you have so many folders of bookmarks that they have turned into a giant mess? Are tags hard to find or too general when you are searching for something? Have trouble finding the right tag? Do you want a neat way to organize things? Introducing TableTags! This presents the theory and a small simple api, called TinyTags, to better organize your data. The code base is tiny, only around 1000 lines of code before unit tests, and it's built on top of a tiny document database called tinydb. It's designed as a simple first attempt to better meet my organizational demands and hopefully promote wide adoption as a better way to organize bookmarks, files, webpages, and really anything where you have a large collection of data you'd like to organize and browze.

# The Problems 

## Folders

So what's wrong with folders? Say you have one folder named, "jumping" where you keep all the things you see that jump and another folder named squirrel where you keep all your squirrel pictures. Now what if you see a jumping squirrel? Which folder do you put it in? One solution to this for each animal have a folder inside called jumping. That way for each animal you see that jumps, you have a place to put it. The problem with this is say you want to see all the jumping animals? You have to search through all the animal folders to find all the subcategories that jump. You can arrange them the other way with jumping and other actions you might want to see as the parent folders, but then you get the reverse problem searching through all the actions to find which ones contain animals. So then we get into keeping both actions as the main category and animals as the main category, but then we have to keep multiple copies of the same file in different locations. If you delete or change the picture in one location, it remains unchanged in the other locations. So you either have to remember and find all the places that contains the picture and change them all, or have a very messy situation. This is the issue with using only folders. So this brings us to tags. They seemed to have been made as a fix to this problem by making a piece of information contain two or more categories, but tags carry their own list of problems. 

## Tags

So what's wrong with tags? The problem is often we can't put related tags into folders, so we get unruly tag clouds where it's hard to find the tag you're looking for. What's more is tags remain simple objects, so we often get tags containing all manner of things. One tag named red will contain all the red things without narrowing down what you actually want to find. So we have to use set operations on tags to narrow down our search. And once again, we are searching for folderless tags to narrow down our search. Sometimes folders and tags can be combined so that we can put tags into folders, but this brings us back to our orginal problem with folders. What if we have a tag named jumping squirrel. Which folder do we put it in. Or we divide our tags up into simple elements, and put them in folders? This seems like a good approach at first until we start dealing with the very complex nature of language. So many words and ideas and tags belong in more than one place, so this brings us back to our orginal problems with folders. And with all these tags, we are still searching through multiple folders to try to find the tags we need to do the set operation that will narrow down our search.

## The current state of affairs

The state of affairs on organization is folders and tags seems to be as far as we've gotten in trying to organize information. From bookmarks to file management to even language, we are in desperate need of a change in the way we organize information that is typically poorly organized with folders and tags. So what do we do about this?

# The Solution

This brings us to something i designed after years of grappling with my own organizational challenges, and stumbling upon good ways of organizing, pulling from several interrelated ideas. It's a merging of folders, tags, and a few more concepts to make something that neither can do well apart but both can do very well together. So simple it's amazing no one has done this before, yet so subtle in it's complexity, it's no wonder no one has done this before(that i know of anyway). It takes the two ways objects can be spatially organized--inside and around, and puts them together. I call them multi-dimentional-table-super-tags, or tabletags for short. So how does it work?

## The four types of containers

There are four types of containers: supertags, taglists, multi-dimentional tables, and tablecells.

All are containers.

Supertags contain supertags and data.
Taglists contain a variety of supertags.
Multi-dimentional tables contains tablecells.
Tablecells contain supertags and data.

Essentially we need classes or to group similar things together. We need a way to group a variety of things together. And we need both simple and complex objects. These concepts can be combined together in a two x two table to make four unique but very interrelated complex containers.

             simple         complex
commonality  supertag       m-table
variation    taglist        tablecell

tags contains commonality of simple
table contains commonality of complex
taglist contains variation of simple
tablecell contains variation of complex

I will use the terms supertags and tags interchangably from now on. They are both the same thing. Regular tags will be used to indicate the commonly found tags out in the wild.

We also find relations diagonally. supertags and tablecells can be named and are sub containers containing the actual data and other tags. Tables and taglists are unnamed and are considered super containers, not to be confused with the super- of supertags.

             named                  unnamed
             sub data containers    super containers
commonality  supertag               m-table
variation    tablecell              taglist

tag and tablecells can be named and are used to store simple and complex tags or data.
table and taglists remain unnamed and are used as super containers of tags and tablecells to show commonalities and variations.

## Supertags

Supertags are called supertags because they aren't your regular tags--they can not only contain data, but can also contain supertags, making them much more like folders than tags. But i call them tags because they can also be combined, like regular tags, to form combinations of tags. There are three types of supertags: tags that contain only other tags, marked with a dot ".tagname"; tags that contain data, marked with a hash "#tagname"; and tags that contain a mix of both or that are empty, marked with neither "tagname".

## Taglists

Taglists are just a number of supertags collected together. The difference between supertags and taglists is supertags contain related data, where as Taglists put together categories that aren't typically related.

## Multi-dimentional tables

Tables are what they sound like. If you've ever worked with an excel sheet or written a table in html, you'll know they are made up of ussually a x by y grid. Tags and taglists can be joined to create a x by y grid of categories. So the children tags of one supertag is put on the x-axis while the children tags of another supertag is put in the y. They are marked by a x: tag1 x tag2. Putting these together makes a number of tablecells that make up complex tags.

.supertag1
    tag1
    tag2

.supertag2
    tag3
    tag4

.supertag1 x .supertag2

     tag1           tag2
tag3 tag1 & tag3    tag2 & tag3
tag4 tag1 & tag4    tag2 & tag4


That handles two dimentional tables, which are the simplist form, but we can go a step further. Lets go into 3D. If we add another supertag which contain a different class of tags to a z dimention, we canstack tables, and create a x by y by z grid.

supertag3
    tag5
    tag6

            tag5
     tag1                   tag2
tag3 tag1 & tag3 & tag5     tag2 & tag3 & tag5
tag4 tag1 & tag4 & tag5     tag2 & tag4 & tag5

            tag6
     tag1                   tag2
tag3 tag1 & tag3 & tag6     tag2 & tag3 & tag6
tag4 tag1 & tag4 & tag6     tag2 & tag4 & tag6

After 3D it gets trickier, but we can do this either by adding supertag4's variations onto the end of tag5 and tag6 so we get four tables, or we use linear variations, like we do in language. Think of each supertag as a dropdown in a list where we select each one. So for example, supertag1dropdown, supertag2dropdown, supertag3dropdown, supertag4dropdown. For each dropdown we select tag1 or tag2, tag3 or tag4, tag5 or tag6, tag7 or tag8 etc...
So we get for this example a 4D multi-dimentional table with 2^4=16 tablecells.
We can calculate the number of tablecells by number-of-tags-in-each-supertag^number-of-super-tags. So say we had a 5D table with two supertags of four child-tags and three supertags with 2 child-tags. That would be 4x4x2x2x2=128 tablecells. As you can see the variation can grow dramatically. Thankfully we are only five choices away from a specific tablecell.

## Tablecells

They are simply the complex of multiple tags put together, much like doing a logical `and` operation on regular tags. They can contain both tags and data. They are marked by a &: as in tag1 & tag2.
