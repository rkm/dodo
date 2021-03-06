% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/list_route.R
\name{list_route}
\alias{list_route}
\title{List an aircraft's route information}
\usage{
list_route(aircraft_id)
}
\arguments{
\item{aircraft_id}{An aircraft ID.}
}
\value{
A list of aircraft route information as a data frame with one row per waypoint
on the route. The row names are waypoint names. If the specified aircraft has
no route, an empty data frame is returned. If the given aircraft ID does
not exist in the simulation, an exception is thrown.
}
\description{
Get the route information of an aircraft as a data frame whose row names are
waypoint names.
}
\examples{
\dontrun{
list_route('ABC123')
}

}
