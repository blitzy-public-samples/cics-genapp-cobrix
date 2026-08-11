******************************************************************
*  COPYBOOK  : GFARR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : AR
******************************************************************
 01  RT-FAR-RATING.

          03 RT-FAR-TERRITORY-CODE            PIC X(3).
          03 RT-FAR-CLASS-CODE                PIC X(4).
          03 RT-FAR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FAR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FAR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FAR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FAR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FAR-RATED-PREMIUM             PIC 9(9)V9(2).
