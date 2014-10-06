Frustrated with the limitations of spreadsheets, we decided to use a customer-relationship management service to help manage our guest list. [Insightly](https://www.insightly.com/) has a good interface and a generous free plan, so we've been using that.

After some experimentation, we decided to use a Contact for a single guest, with separate Contacts for children and +1's so it'd be easy to get counts of attendees. Groups of guests receiving a single invitation share the same Organization, and that Organization's name and address corresponds to how the envelopes will be addressed. We also added some custom fields to help us keep track of things like where people plan to stay. 

At the moment this is just a python script that takes an exported .csv of all of this information from Insightly and reformats it into a .csv that can be uploaded to the printing service Minted. Perhaps I'll add more in the future?

