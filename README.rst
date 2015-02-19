smoking
=======

Ensure the url in sitemaps are correct.

smoking browse the sitemap and create a testsuite containing one test per url
and runnable with nose to get a test result.

So, you can create a job in your preferred CI with test report

::

  $ cd smocking
  $ SITEMAP={sitemap_url} nosetests --with-xunit  --xunit-file=test-reports.xml

