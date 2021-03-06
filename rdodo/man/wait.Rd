% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/wait.R
\name{wait}
\alias{wait}
\title{Wait for a command to take effect}
\usage{
wait(aircraft_id, property, operator = `!=`, initial_value = NULL,
  timeout = 10)
}
\arguments{
\item{aircraft_id}{The aircraft ID.}

\item{property}{The name of the aircraft property to which the change is expected. This must
be one of the column names in the data frame returned by the
\code{\link{aircraft_position}} function (e.g. altitude).}

\item{operator}{A binary operator for testing whether the aircraft property has changed.
Defaults to \code{`!=`}, meaning that the function will return only when the
value of the given property is not equal to its initial (or the timeout is
reached). If an asymmetric operator is used (e.g. \code{`<`}), the initial
value appears on the right-hand side.}

\item{initial_value}{(Optional) The initial value of the property. If omitted, the initial value
is obtained via a call to the \code{\link{aircraft_position}} function.}

\item{timeout}{A timeout after which the function will return even if the expected change
has not been observed.}
}
\value{
Returns \code{TRUE}, invisibly, unless the timeout was reached, in which case
\code{FALSE}.
}
\description{
Wait for a command to take effect
}
